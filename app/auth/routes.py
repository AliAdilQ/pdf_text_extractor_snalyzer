from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from app.auth.forms import LoginForm, PasswordForm, ProfileForm, RegisterForm
from app.extensions import db
from app.models import User, utcnow

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip().lower()
        user = db.session.scalar(
            select(User).where(
                or_(func.lower(User.username) == identity, User.email == identity)
            )
        )
        if user and user.check_password(form.password.data) and user.active:
            login_user(user, remember=form.remember.data)
            user.last_login = utcnow()
            db.session.commit()
            next_url = request.args.get("next", "")
            parts = urlsplit(next_url)
            if (
                not next_url.startswith("/")
                or next_url.startswith("//")
                or parts.netloc
                or parts.scheme
                or "\\" in next_url
            ):
                next_url = url_for("main.dashboard")
            return redirect(next_url)
        flash(
            "Email, username or password is incorrect, or the account is inactive.",
            "danger",
        )
    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        username, email = (
            form.username.data.strip().lower(),
            form.email.data.strip().lower(),
        )
        if db.session.scalar(
            select(User).where(or_(User.username == username, User.email == email))
        ):
            flash("That username or email is already registered.", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("That username or email is already registered.", "danger")
            else:
                login_user(user)
                flash(
                    "Your workspace is ready. Upload your first PDF to get started.",
                    "success",
                )
                return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = ProfileForm(prefix="profile", email=current_user.email)
    password_form = PasswordForm(prefix="password")
    if "profile-submit" in request.form and profile_form.validate_on_submit():
        email = profile_form.email.data.strip().lower()
        existing = db.session.scalar(
            select(User).where(User.email == email, User.id != current_user.id)
        )
        if existing:
            flash("That email belongs to another account.", "danger")
        else:
            current_user.email = email
            try:
                db.session.commit()
                flash("Your profile has been updated.", "success")
            except IntegrityError:
                db.session.rollback()
                flash("That email belongs to another account.", "danger")
    if "password-submit" in request.form and password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("auth.profile"))
        flash("Your current password is incorrect.", "danger")
    return render_template(
        "auth/profile.html", profile_form=profile_form, password_form=password_form
    )
