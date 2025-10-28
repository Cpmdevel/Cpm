from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session, select

DATABASE_URL = "sqlite:///./cinema.db"
engine = create_engine(DATABASE_URL, echo=False)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    is_vip: bool = False
    vip_started_at: Optional[datetime] = None
    vip_expires_at: Optional[datetime] = None


class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    url: str  # Streaming URL or file path


class Subtitle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movie.id")
    language: str = Field(index=True)
    content_srt: str  # raw SRT text


def init_db():
    SQLModel.metadata.create_all(engine)


def seed_data():
    with Session(engine) as session:
        # Only seed once
        has_any = session.exec(select(Movie).limit(1)).first()
        if has_any:
            return
        movie = Movie(title="Sample Chinese Movie", description="Жишээ кино", url="https://example.com/stream/sample.mp4")
        session.add(movie)
        session.flush()
        srt = """1\n00:00:01,000 --> 00:00:04,000\nСайн байна уу?\n\n2\n00:00:05,000 --> 00:00:08,000\nЭнэ бол жишээ хадмал.\n"""
        subtitle = Subtitle(movie_id=movie.id, language="mn", content_srt=srt)
        session.add(subtitle)
        session.commit()
