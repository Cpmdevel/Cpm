from __future__ import annotations

from . import db
from .models import Movie, Subtitle


def seed_demo_content() -> None:
    """Seed one demo Chinese movie with Mongolian subtitles if none exist."""
    if Movie.query.count() > 0:
        return

    movie = Movie(
        title="样片：示例电影 (Sample Chinese Movie)",
        description=(
            "Жишээ кино. VIP-с хамаарч хандалтыг хянах боломжтой. "
            "Доорх видео нь нийтэд нээлттэй жишээ бичлэг юм."
        ),
        # Public sample video (Google GCS sample)
        video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        is_vip_only=True,
    )
    db.session.add(movie)
    db.session.flush()

    sub = Subtitle(
        movie_id=movie.id,
        lang="mn",
        label="Монгол",
        file_path="subtitles/mn_sample.vtt",
    )
    db.session.add(sub)
    db.session.commit()
