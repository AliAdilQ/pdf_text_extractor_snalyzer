"""Atomic document ingestion and filesystem cleanup."""

from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Analysis, Document
from app.utils.pdf_extractor import PDFExtractionError, extract_pdf
from app.utils.text_analyzer import analyze_text


def create_document(file, user_id: int) -> Document:
    """Validate, store, extract and analyze; remove the file on any failed transaction."""
    original = secure_filename(file.filename or "")[:255]
    if not original or not original.lower().endswith(".pdf"):
        raise PDFExtractionError("Please choose a file with a .pdf extension.")
    if file.mimetype not in {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
        "",
    }:
        raise PDFExtractionError(
            "The selected file isn't a PDF. Please check its format."
        )
    stored = f"{uuid4().hex}.pdf"
    path = Path(current_app.config["UPLOAD_FOLDER"]) / stored
    try:
        file.save(path)
        if path.stat().st_size > current_app.config["MAX_CONTENT_LENGTH"]:
            raise PDFExtractionError("This file exceeds the configured upload limit.")
        result = extract_pdf(
            path,
            current_app.config["MAX_PDF_PAGES"],
            current_app.config["MAX_EXTRACTED_CHARACTERS"],
        )
        stats = analyze_text("\n\n".join(result.pages))
        columns = (
            "word_count",
            "character_count",
            "sentence_count",
            "paragraph_count",
            "unique_word_count",
            "reading_time",
        )
        document = Document(
            original_filename=original,
            stored_filename=stored,
            user_id=user_id,
            file_size=path.stat().st_size,
            page_count=len(result.pages),
            page_texts=result.pages,
            status="no_text" if result.warning else "analyzed",
            warning=result.warning,
            extraction_method=result.method,
            **{key: stats[key] for key in columns},
        )
        analysis_columns = (
            "keywords",
            "common_words",
            "longest_words",
            "shortest_words",
            "lexical_diversity",
            "average_word_length",
            "average_sentence_length",
            "characters_without_spaces",
        )
        document.analysis = Analysis(**{key: stats[key] for key in analysis_columns})
        db.session.add(document)
        db.session.commit()
        return document
    except Exception:
        db.session.rollback()
        path.unlink(missing_ok=True)
        raise


def delete_document(document):
    path = Path(current_app.config["UPLOAD_FOLDER"]) / document.stored_filename
    db.session.delete(document)
    db.session.commit()
    try:
        path.unlink(missing_ok=True)
    except OSError:
        current_app.logger.exception("Unable to remove an orphaned uploaded file")
