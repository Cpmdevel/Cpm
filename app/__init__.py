from __future__ import annotations

import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Global extensions
# These are initialized without an app and later bound in create_app
# to keep import order simple.
db = SQLAlchemy()
login_manager = LoginManager()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Basic configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Use SQLite by default; can be overridden with DATABASE_URL
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    # Redirect unauthenticated users here
    login_manager.login_view = "main.login"

    # Import models so SQLAlchemy knows about them
    from . import models  # noqa: F401

    # Register routes blueprint
    from .routes import bp as main_bp  # noqa: E402
    app.register_blueprint(main_bp)

    return app


def initialize_database(app: Flask) -> None:
    """Create all tables if they do not exist."""
    with app.app_context():
        db.create_all()


@login_manager.user_loader
def load_user(user_id: str):
    from .models import User  # local import to avoid circular deps
    try:
        int_id = int(user_id)
    except (TypeError, ValueError):
        return None
    return User.query.get(int_id)
