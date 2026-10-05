"""Flask application factory."""

import secrets
from pathlib import Path

from flask import Flask, render_template
from flask_login import current_user, logout_user
from flask_wtf.csrf import CSRFError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection

from app.extensions import csrf, db, login_manager, migrate
from config import Config


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, _):
    if isinstance(connection, Connection):
        connection.execute("PRAGMA foreign_keys=ON")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if app.config["APP_ENV"] == "production" and (
        not app.config["SECRET_KEY"]
        or app.config["SECRET_KEY"] == "change-this-secret-key"
    ):
        raise RuntimeError("Set a unique SECRET_KEY before running in production.")
    if not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = secrets.token_hex(32)
        app.logger.warning(
            "Using a temporary development secret. Set SECRET_KEY in .env for persistent sessions."
        )
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    from app.models import User
    from app.auth.routes import bp as auth_bp
    from app.main.routes import bp as main_bp
    from app.documents.routes import bp as documents_bp
    from app.admin.routes import bp as admin_bp
    from app.cli import register_commands

    for blueprint in (auth_bp, main_bp, documents_bp, admin_bp):
        app.register_blueprint(blueprint)
    register_commands(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = db.session.get(User, int(user_id))
            return user if user and user.active else None
        except (ValueError, TypeError):
            return None

    @app.before_request
    def check_active_account():
        if current_user.is_authenticated and not current_user.active:
            logout_user()

    @app.template_filter("number")
    def number(value):
        return f"{value or 0:,}"

    @app.template_filter("filesize")
    def filesize(value):
        return (
            f"{value / 1048576:.1f} MB"
            if value >= 1048576
            else f"{value / 1024:.1f} KB"
        )

    @app.context_processor
    def shared_context():
        return {"max_upload_mb": app.config["MAX_CONTENT_LENGTH"] / 1048576}

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if current_user.is_authenticated:
            response.headers["Cache-Control"] = "no-store"
        return response

    messages = {
        403: (
            "Access restricted",
            "Your account doesn't have permission to visit this page.",
        ),
        404: (
            "A page out of place",
            "We couldn't find that page or document. Let's get you back on track.",
        ),
        413: (
            "This file is a little too big",
            f"Please choose a PDF smaller than {app.config['MAX_CONTENT_LENGTH'] / 1048576:g} MB.",
        ),
        500: (
            "Something went wrong",
            "We couldn't complete that request. Please try again.",
        ),
    }

    def error_page(error):
        code = getattr(error, "code", 500)
        if code == 500:
            db.session.rollback()
        title, message = messages.get(
            code,
            (
                "Request could not be completed",
                "Please refresh the page and try again.",
            ),
        )
        return render_template(
            "errors/error.html", code=code, title=title, message=message
        ), code

    for code in messages:
        app.register_error_handler(code, error_page)

    @app.errorhandler(CSRFError)
    def csrf_error(_):
        return render_template(
            "errors/error.html",
            code=400,
            title="Your session needs a refresh",
            message="Refresh the page before submitting the form again.",
        ), 400

    return app
