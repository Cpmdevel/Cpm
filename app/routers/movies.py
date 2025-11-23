from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import engine, Movie, Subtitle
from .auth import get_current_user, get_session

router = APIRouter()


@router.get("/")
def list_movies(session: Session = Depends(get_session)):
    movies = session.exec(select(Movie)).all()
    return [{"id": m.id, "title": m.title, "description": m.description} for m in movies]


@router.get("/{movie_id}")
def get_movie(movie_id: int, session: Session = Depends(get_session)):
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"id": movie.id, "title": movie.title, "description": movie.description, "url": movie.url}


@router.get("/{movie_id}/subtitles")
def get_subtitles(movie_id: int, lang: str = "mn", session: Session = Depends(get_session)):
    srt = session.exec(select(Subtitle).where(Subtitle.movie_id == movie_id, Subtitle.language == lang)).first()
    if not srt:
        raise HTTPException(status_code=404, detail="Subtitles not found")
    return {"language": srt.language, "content_srt": srt.content_srt}


@router.get("/{movie_id}/play")
def play_movie(movie_id: int, user=Depends(get_current_user), session: Session = Depends(get_session)):
    # VIP-only access to play
    from datetime import datetime

    if not user.is_vip or not user.vip_expires_at or user.vip_expires_at <= datetime.utcnow():
        raise HTTPException(status_code=402, detail="VIP subscription required")
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"stream_url": movie.url}
