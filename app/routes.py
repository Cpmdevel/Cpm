from __future__ import annotations

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import User, Movie, Subtitle, create_or_extend_subscription

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    return render_template("index.html", movies=movies)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        if not email or not password:
            flash("Please provide email and password.", "warning")
            return redirect(url_for("main.register"))
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email is already registered.", "danger")
            return redirect(url_for("main.login"))
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("main.login"))
        login_user(user)
        flash("Welcome back!", "success")
        next_url = request.args.get("next") or url_for("main.index")
        return redirect(next_url)
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/vip")
@login_required
def vip():
    active = current_user.active_subscription()
    return render_template("vip.html", active=active)


@bp.route("/vip/purchase", methods=["POST"]) 
@login_required
def purchase_vip():
    # Simple purchase simulation: activate or extend 30 days
    _ = create_or_extend_subscription(current_user, days=30, plan_name="VIP-30")
    flash("VIP activated! Your subscription starts counting from your payment day.", "success")
    return redirect(url_for("main.vip"))


@bp.route("/watch/<int:movie_id>")
@login_required
def watch(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    if movie.is_vip_only and not current_user.has_active_vip():
        flash("This movie is VIP-only. Please activate VIP to watch.", "warning")
        return redirect(url_for("main.vip"))

    # Prefer Mongolian subtitles if present
    subs = [s for s in movie.subtitles if s.lang.lower() == "mn"] or movie.subtitles
    return render_template("watch.html", movie=movie, subtitles=subs)
