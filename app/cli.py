"""Explicit local demo setup; demo credentials are never part of authentication logic."""

from datetime import timedelta

import click
from sqlalchemy import select
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.documents.services import create_document
from app.extensions import db
from app.models import Document, User, utcnow
from config import ROOT
from tools.generate_samples import generate_samples


def seed_demo():
    """Idempotently add demo accounts and real analyses of original sample PDFs."""
    from flask import current_app

    if current_app.config["APP_ENV"] == "production":
        raise click.ClickException("Demo seeding is disabled in production.")
    for username, email, password, role in [
        ("admin", "admin@example.com", "Admin123!", "admin"),
        ("demo", "demo@example.com", "Demo123!", "user"),
    ]:
        user = db.session.scalar(select(User).where(User.username == username))
        if not user:
            if db.session.scalar(select(User).where(User.email == email)):
                raise click.ClickException(
                    f"The demo email {email} is already in use. No existing account was changed."
                )
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
    db.session.commit()
    demo = db.session.scalar(select(User).where(User.username == "demo"))
    if not demo.check_password("Demo123!"):
        click.echo(
            "Existing demo password was preserved; it may differ from the documented demo password."
        )
    sample_paths = sorted((ROOT / "sample_data").glob("*.pdf"))
    if len(sample_paths) < 5:
        sample_paths = generate_samples()
    added = 0
    for index, path in enumerate(sample_paths):
        name = secure_filename(path.name)
        if db.session.scalar(
            select(Document).where(
                Document.user_id == demo.id, Document.original_filename == name
            )
        ):
            continue
        with path.open("rb") as stream:
            document = create_document(
                FileStorage(
                    stream=stream, filename=path.name, content_type="application/pdf"
                ),
                demo.id,
            )
        document.created_at = utcnow() - timedelta(days=index, hours=2 + index)
        document.analysis.created_at = document.created_at
        db.session.commit()
        added += 1
    click.echo(
        f"Demo ready: added {added} documents. Existing accounts and passwords were preserved."
    )


def register_commands(app):
    @app.cli.command("seed-demo")
    def seed_command():
        """Create local demo accounts and five original PDF analyses after db upgrade."""
        seed_demo()
