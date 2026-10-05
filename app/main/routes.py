from datetime import timedelta

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func, select

from app.extensions import db
from app.models import Document, utcnow
from app.utils.helpers import document_totals

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    return render_template("home.html")


@bp.get("/dashboard")
@login_required
def dashboard():
    documents = db.session.scalars(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .limit(5)
    ).all()
    recent = db.session.scalar(
        select(func.count(Document.id)).where(
            Document.user_id == current_user.id,
            Document.created_at >= utcnow() - timedelta(days=7),
        )
    )
    totals = document_totals(current_user.id)
    totals["recent"] = recent
    return render_template("dashboard/index.html", documents=documents, totals=totals)
