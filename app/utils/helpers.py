from functools import wraps

from flask import abort
from flask_login import current_user, login_required
from sqlalchemy import func, select

from app.extensions import db
from app.models import Document


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def document_for_user(document_id):
    document = db.get_or_404(Document, document_id)
    if document.user_id != current_user.id and not current_user.is_admin:
        abort(404)
    return document


def document_totals(user_id=None):
    query = select(
        func.count(Document.id),
        func.coalesce(func.sum(Document.page_count), 0),
        func.coalesce(func.sum(Document.word_count), 0),
    )
    if user_id is not None:
        query = query.where(Document.user_id == user_id)
    documents, pages, words = db.session.execute(query).one()
    return {"documents": documents, "pages": pages, "words": words}
