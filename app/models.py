from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plan_name = db.Column(db.String(64), nullable=False, default="VIP")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def is_active(self) -> bool:
        today = date.today()
        return self.end_date >= today


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    subscriptions = db.relationship(Subscription, backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        # Explicit str for Flask-Login
        return str(self.id)

    def active_subscription(self) -> Optional[Subscription]:
        today = date.today()
        return (
            self.subscriptions
            .filter(Subscription.end_date >= today)
            .order_by(Subscription.end_date.desc())
            .first()
        )

    def has_active_vip(self) -> bool:
        sub = self.active_subscription()
        return bool(sub and sub.is_active)


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(2048), nullable=False)
    is_vip_only = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    subtitles = db.relationship("Subtitle", backref="movie", lazy="joined", cascade="all, delete-orphan")


class Subtitle(db.Model):
    __tablename__ = "subtitles"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False, index=True)
    lang = db.Column(db.String(16), nullable=False, index=True)
    label = db.Column(db.String(64), nullable=False)
    # Path relative to the Flask static folder, e.g., "subtitles/mn_sample.vtt"
    file_path = db.Column(db.String(512), nullable=False)

    @property
    def file_path_rel(self) -> str:
        return self.file_path


def create_or_extend_subscription(user: User, days: int = 30, plan_name: str = "VIP") -> Subscription:
    """Create a subscription starting today or extend the current one.

    - If the user has an active subscription, extend from its current end_date.
    - Otherwise, start counting from today (the payment day).
    """
    today = date.today()
    active = user.active_subscription()
    if active:
        new_start = active.start_date
        new_end = active.end_date + timedelta(days=days)
        active.end_date = new_end
        db.session.add(active)
        db.session.commit()
        return active

    # No active subscription: starts counting from today (payment day)
    sub = Subscription(
        user=user,
        plan_name=plan_name,
        start_date=today,
        end_date=today + timedelta(days=days),
    )
    db.session.add(sub)
    db.session.commit()
    return sub
