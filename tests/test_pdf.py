from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.extensions import db
from app.models import Analysis, Document
from app.utils.pdf_extractor import PDFExtractionError, extract_pdf
from app.utils.text_analyzer import analyze_text, search_text


def test_analyzer():
    result = analyze_text(
        "Python builds tools. Python builds insight!\n\nThe tools help people."
    )
    assert result["word_count"] == 10
    assert result["unique_word_count"] == 7
    assert result["sentence_count"] == 3
    assert result["paragraph_count"] == 2
    assert result["reading_time"] == 0.05
    assert "the" not in {item["word"] for item in result["keywords"]}
    assert result["keywords"][0] == {"word": "python", "count": 2}


def test_empty_analyzer():
    result = analyze_text("")
    assert result["word_count"] == result["lexical_diversity"] == 0
    assert result["keywords"] == []


def test_unicode_and_no_network_needed():
    result = analyze_text("Café café naïve! don't stop.")
    assert result["word_count"] == 5
    assert result["unique_word_count"] == 4


def test_literal_search():
    result = search_text("Python python PYTHON [x]", "python")
    assert result["count"] == 3
    assert search_text("[x] x", "[x]")["count"] == 1


def test_upload_extract_and_analysis(upload, app):
    assert upload.status_code == 302
    with app.app_context():
        document = db.session.query(Document).one()
        assert document.page_count == 2
        assert "Python" in document.extracted_text
        assert document.word_count > 20
        assert document.analysis.keywords
        assert (Path(app.config["UPLOAD_FOLDER"]) / document.stored_filename).exists()


@pytest.mark.parametrize(
    "filename,mime,contents",
    [
        ("notes.txt", "text/plain", b"hello"),
        ("bad.pdf", "application/pdf", b"not a pdf"),
        ("bad.pdf", "image/png", b"%PDF-fake"),
    ],
)
def test_reject_invalid_uploads(client, login, app, filename, mime, contents):
    login()
    response = client.post("/upload", data={"pdf": (BytesIO(contents), filename, mime)})
    assert response.status_code == 200
    with app.app_context():
        assert db.session.query(Document).count() == 0
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []


def test_encrypted_and_zero_page_pdf(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.encrypt("password")
    encrypted = tmp_path / "encrypted.pdf"
    writer.write(encrypted)
    with pytest.raises(PDFExtractionError, match="encrypted"):
        extract_pdf(encrypted)
    empty = tmp_path / "empty.pdf"
    PdfWriter().write(empty)
    with pytest.raises(PDFExtractionError, match="no pages"):
        extract_pdf(empty)


def test_scanned_pdf_warning(client, login, app):
    login()
    stream = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.write(stream)
    stream.seek(0)
    response = client.post("/upload", data={"pdf": (stream, "scan.pdf")})
    assert response.status_code == 302
    with app.app_context():
        document = db.session.query(Document).one()
        assert document.status == "no_text"
        assert "scanned images" in document.warning


def test_resource_limits(tmp_path, pdf_bytes):
    path = tmp_path / "notes.pdf"
    path.write_bytes(pdf_bytes)
    with pytest.raises(PDFExtractionError, match="page limit"):
        extract_pdf(path, max_pages=1)
    with pytest.raises(PDFExtractionError, match="too much text"):
        extract_pdf(path, max_characters=5)


def test_oversized_request(client, login, app):
    login()
    app.config["MAX_CONTENT_LENGTH"] = 1024
    response = client.post("/upload", data={"pdf": (BytesIO(b"x" * 2048), "large.pdf")})
    assert response.status_code == 413


def test_export_search_delete(client, upload, app):
    document_url = upload.location
    assert b"2 matches" in client.get(document_url + "?q=python").data
    assert b"<mark>Python</mark>" in client.get(document_url + "?q=python").data
    text = client.get(document_url + "/export/txt")
    assert text.status_code == 200 and b"Python" in text.data
    assert "notes_extracted.txt" in text.headers["Content-Disposition"]
    assert b"Statistic,Value" in client.get(document_url + "/export/csv").data
    assert client.post(document_url + "/delete").status_code == 302
    with app.app_context():
        assert (
            db.session.query(Document).count()
            == db.session.query(Analysis).count()
            == 0
        )
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []
