"""Persistent accounts, documents and their analysis."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="user")
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    last_login = db.Column(db.DateTime(timezone=True))
    documents = db.relationship(
        "Document", back_populates="owner", cascade="all, delete-orphan"
    )

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.role == "admin"

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(100), nullable=False, unique=True)
    file_size = db.Column(db.Integer, nullable=False)
    page_count = db.Column(db.Integer, nullable=False)
    page_texts = db.Column(db.JSON, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    character_count = db.Column(db.Integer, nullable=False)
    sentence_count = db.Column(db.Integer, nullable=False)
    paragraph_count = db.Column(db.Integer, nullable=False)
    unique_word_count = db.Column(db.Integer, nullable=False)
    reading_time = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="analyzed")
    extraction_method = db.Column(db.String(30), nullable=False)
    warning = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    owner = db.relationship("User", back_populates="documents")
    analysis = db.relationship(
        "Analysis",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def extracted_text(self):
        # Page text is the source of truth; do not store a duplicate full copy.
        return "\n\n".join(self.page_texts)


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer, db.ForeignKey("document.id"), unique=True, nullable=False
    )
    keywords = db.Column(db.JSON, nullable=False)
    common_words = db.Column(db.JSON, nullable=False)
    longest_words = db.Column(db.JSON, nullable=False)
    shortest_words = db.Column(db.JSON, nullable=False)
    lexical_diversity = db.Column(db.Float, nullable=False)
    average_word_length = db.Column(db.Float, nullable=False)
    average_sentence_length = db.Column(db.Float, nullable=False)
    characters_without_spaces = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    document = db.relationship("Document", back_populates="analysis")
