from contextlib import asynccontextmanager
from fastapi import FastAPI

from .routers import auth, movies
from .db import init_db, seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_data()
    yield


app = FastAPI(title="Cinema API", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(movies.router, prefix="/movies", tags=["movies"])


@app.get("/")
async def root():
    return {"ok": True, "service": "Cinema API"}
