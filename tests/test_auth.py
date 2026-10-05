from app.extensions import db
from app.models import User


def test_registration(client, app):
    response = client.post(
        "/register",
        data={
            "username": "new_user",
            "email": "new@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        user = db.session.query(User).filter_by(username="new_user").one()
        assert user.check_password("Password123!")
        assert user.password_hash != "Password123!"
        assert user.role == "user"


def test_duplicate_registration_case_insensitive(client, app):
    response = client.post(
        "/register",
        data={
            "username": "ALICE",
            "email": "other@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    assert b"already registered" in response.data
    with app.app_context():
        assert db.session.query(User).count() == 3


def test_login_and_logout(client, login):
    assert login().status_code == 302
    assert client.get("/dashboard").status_code == 200
    assert client.post("/logout").status_code == 302
    assert client.get("/dashboard").status_code == 302
    assert client.get("/logout").status_code == 405


def test_invalid_login(client):
    response = client.post("/login", data={"identity": "alice", "password": "wrong"})
    assert b"incorrect" in response.data
    assert client.get("/dashboard").status_code == 302


def test_email_login_remember_and_last_login(client, app):
    response = client.post(
        "/login",
        data={
            "identity": "ALICE@example.com",
            "password": "StrongPass123!",
            "remember": "y",
        },
    )
    assert "remember_token=" in ";".join(response.headers.getlist("Set-Cookie"))
    with app.app_context():
        assert db.session.query(User).filter_by(username="alice").one().last_login


def test_no_open_redirect(client):
    response = client.post(
        "/login?next=//evil.example",
        data={"identity": "alice", "password": "StrongPass123!"},
    )
    assert response.location == "/dashboard"


def test_inactive_user_cannot_login(client, app):
    with app.app_context():
        db.session.query(User).filter_by(username="alice").one().active = False
        db.session.commit()
    client.post("/login", data={"identity": "alice", "password": "StrongPass123!"})
    assert client.get("/dashboard").status_code == 302


def test_password_change(client, login, app):
    login()
    response = client.post(
        "/profile",
        data={
            "password-current_password": "StrongPass123!",
            "password-new_password": "UpdatedPass123!",
            "password-confirm_password": "UpdatedPass123!",
            "password-submit": "Update password",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        assert (
            db.session.query(User)
            .filter_by(username="alice")
            .one()
            .check_password("UpdatedPass123!")
        )


def test_csrf_required(client, app):
    app.config["WTF_CSRF_ENABLED"] = True
    assert (
        client.post(
            "/login", data={"identity": "alice", "password": "StrongPass123!"}
        ).status_code
        == 400
    )
