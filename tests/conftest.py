from io import BytesIO
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from app import create_app
from app.extensions import db
from app.models import User


def pytest_configure():
    # Pytest's explicit base directory needs an existing parent on Windows.
    (Path(__file__).resolve().parents[1] / "tmp").mkdir(exist_ok=True)


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-only",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "WTF_CSRF_ENABLED": False,
        }
    )
    with application.app_context():
        db.create_all()
        for username, role in [("alice", "user"), ("bob", "user"), ("admin", "admin")]:
            user = User(username=username, email=f"{username}@example.com", role=role)
            user.set_password("StrongPass123!")
            db.session.add(user)
        db.session.commit()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    def sign_in(username="alice"):
        return client.post(
            "/login", data={"identity": username, "password": "StrongPass123!"}
        )

    return sign_in


@pytest.fixture
def pdf_bytes():
    stream = BytesIO()
    pdf = canvas.Canvas(stream)
    pdf.drawString(
        72, 750, "Python analysis reveals patterns. Python makes data useful."
    )
    pdf.drawString(72, 725, "Searchable text belongs in a private document workspace.")
    pdf.showPage()
    pdf.drawString(72, 750, "Reliable software protects every document and every user.")
    pdf.save()
    return stream.getvalue()


@pytest.fixture
def upload(client, login, pdf_bytes):
    login()
    return client.post(
        "/upload",
        data={"pdf": (BytesIO(pdf_bytes), "notes.pdf")},
        content_type="multipart/form-data",
    )
