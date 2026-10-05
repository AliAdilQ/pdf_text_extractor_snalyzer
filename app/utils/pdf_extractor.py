"""PDF extraction with page and text limits, plus a pdfplumber fallback."""

from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


class PDFExtractionError(ValueError):
    """An actionable, safe-to-display PDF validation error."""


@dataclass
class ExtractedPDF:
    pages: list[str]
    method: str
    warning: str | None = None


def extract_pdf(
    path: Path, max_pages: int = 300, max_characters: int = 2000000
) -> ExtractedPDF:
    with path.open("rb") as stream:
        if not stream.read(1024).lstrip().startswith(b"%PDF-"):
            raise PDFExtractionError(
                "This file isn't a valid PDF. Please export it as a PDF and try again."
            )
    try:
        reader = PdfReader(path, strict=False)
        if reader.is_encrypted:
            raise PDFExtractionError(
                "This PDF is encrypted. Upload an unprotected copy to extract its text."
            )
        page_count = len(reader.pages)
        if not page_count:
            raise PDFExtractionError(
                "This PDF has no pages. Please choose another document."
            )
        if page_count > max_pages:
            raise PDFExtractionError(f"This PDF exceeds the {max_pages}-page limit.")
        pages, total = [], 0
        for page in reader.pages:
            text = (page.extract_text() or "").replace("\x00", "").strip()
            total += len(text)
            if total > max_characters:
                raise PDFExtractionError(
                    "This PDF contains too much text to process. Please split it into smaller documents."
                )
            pages.append(text)
        if any(pages):
            return ExtractedPDF(pages, "pypdf")
    except PDFExtractionError:
        raise
    except Exception:
        pages = None
    try:
        with pdfplumber.open(path) as pdf:
            if not pdf.pages:
                raise PDFExtractionError(
                    "This PDF has no pages. Please choose another document."
                )
            if len(pdf.pages) > max_pages:
                raise PDFExtractionError(
                    f"This PDF exceeds the {max_pages}-page limit."
                )
            pages, total = [], 0
            for page in pdf.pages:
                text = (page.extract_text() or "").replace("\x00", "").strip()
                total += len(text)
                if total > max_characters:
                    raise PDFExtractionError(
                        "This PDF contains too much text to process. Please split it into smaller documents."
                    )
                pages.append(text)
        warning = (
            None
            if any(pages)
            else "This PDF appears to contain scanned images or non-extractable text."
        )
        return ExtractedPDF(pages, "pdfplumber", warning)
    except PDFExtractionError:
        raise
    except Exception as error:
        raise PDFExtractionError(
            "We couldn't read this PDF. It may be corrupted; try exporting a fresh copy."
        ) from error
