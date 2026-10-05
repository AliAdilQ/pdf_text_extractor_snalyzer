from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Analysis, Document, User
from app.utils.helpers import admin_required, document_totals

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("")
@bp.get("/")
@admin_required
def dashboard():
    totals = document_totals()
    totals["users"] = db.session.scalar(select(func.count(User.id)))
    users = db.session.scalars(
        select(User).order_by(User.created_at.desc()).limit(5)
    ).all()
    documents = db.session.scalars(
        select(Document).order_by(Document.created_at.desc()).limit(5)
    ).all()
    return render_template(
        "admin/dashboard.html", totals=totals, users=users, documents=documents
    )


@bp.get("/users")
@admin_required
def users():
    q = request.args.get("q", "").strip()[:100]
    query = select(User)
    if q:
        query = query.where(
            or_(User.username.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
        )
    pagination = db.paginate(
        query.order_by(User.created_at.desc()),
        page=request.args.get("page", 1, type=int),
        per_page=10,
        error_out=False,
    )
    return render_template("admin/users.html", pagination=pagination, q=q)


@bp.get("/users/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = db.get_or_404(User, user_id)
    documents = db.session.scalars(
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
        .limit(10)
    ).all()
    return render_template(
        "admin/user.html",
        user=user,
        documents=documents,
        totals=document_totals(user.id),
    )


@bp.post("/users/<int:user_id>/manage")
@admin_required
def manage_user(user_id):
    user = db.get_or_404(User, user_id)
    action = request.form.get("action")
    if action not in ("role", "toggle", "delete"):
        abort(400)
    if user.id == current_user.id:
        flash(
            "Manage your own profile from Account settings. You cannot disable, demote or delete your own admin account.",
            "warning",
        )
        return redirect(url_for("admin.user_detail", user_id=user.id))
    active_admins = db.session.scalar(
        select(func.count(User.id)).where(User.role == "admin", User.active.is_(True))
    )
    if user.is_admin and user.active and active_admins <= 1:
        flash("Keep at least one active administrator.", "warning")
        return redirect(url_for("admin.user_detail", user_id=user.id))
    files = []
    if action == "role":
        role = request.form.get("role")
        if role not in ("user", "admin"):
            abort(400)
        user.role = role
    elif action == "toggle":
        user.active = not user.active
    else:
        files = [
            Path(current_app.config["UPLOAD_FOLDER"]) / document.stored_filename
            for document in user.documents
        ]
        db.session.delete(user)
    db.session.commit()
    for path in files:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            current_app.logger.exception("Unable to remove an orphaned uploaded file")
    flash(
        "Account updated."
        if action != "delete"
        else "Account and all its documents deleted.",
        "success",
    )
    return redirect(url_for("admin.users"))


@bp.get("/documents")
@admin_required
def documents():
    q = request.args.get("q", "").strip()[:100]
    query = select(Document).join(User)
    if q:
        query = query.where(
            or_(
                Document.original_filename.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%"),
            )
        )
    pagination = db.paginate(
        query.order_by(Document.created_at.desc()),
        page=request.args.get("page", 1, type=int),
        per_page=10,
        error_out=False,
    )
    return render_template("admin/documents.html", pagination=pagination, q=q)


@bp.get("/analyses")
@admin_required
def analyses():
    pagination = db.paginate(
        select(Analysis).order_by(Analysis.created_at.desc()),
        page=request.args.get("page", 1, type=int),
        per_page=10,
        error_out=False,
    )
    return render_template("admin/analyses.html", pagination=pagination)
