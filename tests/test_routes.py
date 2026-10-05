import pytest

from app.extensions import db
from app.models import User


@pytest.mark.parametrize("route", ["/", "/login", "/register"])
def test_public_pages(client, route):
    assert client.get(route).status_code == 200


@pytest.mark.parametrize(
    "route",
    [
        "/dashboard",
        "/documents",
        "/upload",
        "/profile",
        "/admin",
        "/admin/users",
        "/admin/documents",
        "/admin/analyses",
    ],
)
def test_protected_routes(client, route):
    assert client.get(route).status_code == 302


@pytest.mark.parametrize(
    "route",
    ["/admin", "/admin/users", "/admin/documents", "/admin/analyses", "/admin/users/1"],
)
def test_admin_authorization(client, login, route):
    login()
    assert client.get(route).status_code == 403


def test_admin_routes_and_own_account_safety(client, login, app):
    login("admin")
    for route in ["/admin", "/admin/users", "/admin/documents", "/admin/analyses"]:
        assert client.get(route).status_code == 200
    with app.app_context():
        admin_id = db.session.query(User).filter_by(username="admin").one().id
    client.post(f"/admin/users/{admin_id}/manage", data={"action": "delete"})
    with app.app_context():
        assert db.session.get(User, admin_id).active


def test_document_ownership_all_actions(client, upload):
    url = upload.location
    client.post("/logout")
    client.post("/login", data={"identity": "bob", "password": "StrongPass123!"})
    assert client.get(url).status_code == 404
    assert client.get(url + "/export/txt").status_code == 404
    assert client.get(url + "/export/csv").status_code == 404
    assert client.post(url + "/delete").status_code == 404
    assert b"notes.pdf" not in client.get("/documents").data


def test_admin_can_review_other_documents(client, upload):
    url = upload.location
    client.post("/logout")
    client.post("/login", data={"identity": "admin", "password": "StrongPass123!"})
    assert client.get(url).status_code == 200
    assert b"notes.pdf" in client.get("/admin/documents").data


def test_deactivation_revokes_session(client, login, app):
    login()
    with app.app_context():
        db.session.query(User).filter_by(username="alice").one().active = False
        db.session.commit()
    assert client.get("/dashboard").status_code == 302


def test_admin_delete_user_cascades_files(client, upload, app):
    from pathlib import Path
    from app.models import Analysis, Document

    with app.app_context():
        alice_id = db.session.query(User).filter_by(username="alice").one().id
    client.post("/logout")
    client.post("/login", data={"identity": "admin", "password": "StrongPass123!"})
    assert (
        client.post(
            f"/admin/users/{alice_id}/manage", data={"action": "delete"}
        ).status_code
        == 302
    )
    with app.app_context():
        assert db.session.get(User, alice_id) is None
        assert (
            db.session.query(Document).count()
            == db.session.query(Analysis).count()
            == 0
        )
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []


def test_styled_not_found(client):
    response = client.get("/missing")
    assert response.status_code == 404
    assert b"A page out of place" in response.data
