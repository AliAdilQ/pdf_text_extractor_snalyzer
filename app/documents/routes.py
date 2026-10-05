import csv
from io import BytesIO, StringIO
from pathlib import Path

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import select
from werkzeug.utils import secure_filename

from app.documents.forms import UploadForm
from app.documents.services import create_document, delete_document
from app.extensions import db
from app.models import Document
from app.utils.helpers import document_for_user
from app.utils.pdf_extractor import PDFExtractionError
from app.utils.text_analyzer import search_text

bp = Blueprint("documents", __name__)


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            document = create_document(form.pdf.data, current_user.id)
        except PDFExtractionError as error:
            flash(str(error), "danger")
        else:
            flash(
                document.warning or "Your PDF has been extracted and analyzed.",
                "warning" if document.warning else "success",
            )
            return redirect(url_for("documents.detail", document_id=document.id))
    return render_template("documents/upload.html", form=form)


@bp.get("/documents")
@login_required
def index():
    query_text = request.args.get("q", "").strip()[:100]
    status = request.args.get("status", "")
    sort = request.args.get("sort", "newest")
    query = select(Document).where(Document.user_id == current_user.id)
    if query_text:
        query = query.where(
            Document.original_filename.icontains(query_text, autoescape=True)
        )
    if status in ("analyzed", "no_text"):
        query = query.where(Document.status == status)
    ordering = {
        "newest": Document.created_at.desc(),
        "oldest": Document.created_at.asc(),
        "name": Document.original_filename.asc(),
        "words": Document.word_count.desc(),
    }
    query = query.order_by(ordering.get(sort, ordering["newest"]), Document.id.desc())
    pagination = db.paginate(
        query, page=request.args.get("page", 1, type=int), per_page=10, error_out=False
    )
    return render_template(
        "documents/index.html",
        pagination=pagination,
        q=query_text,
        status=status,
        sort=sort,
    )


@bp.get("/documents/<int:document_id>")
@login_required
def detail(document_id):
    document = document_for_user(document_id)
    search = search_text(document.extracted_text, request.args.get("q", ""))
    return render_template("documents/detail.html", document=document, search=search)


@bp.get("/documents/<int:document_id>/export/<format>")
@login_required
def export(document_id, format):
    document = document_for_user(document_id)
    stem = secure_filename(Path(document.original_filename).stem) or "document"
    if format == "txt":
        content, mimetype, filename = (
            document.extracted_text,
            "text/plain; charset=utf-8",
            f"{stem}_extracted.txt",
        )
    elif format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Statistic", "Value"])
        for key in (
            "page_count",
            "word_count",
            "character_count",
            "sentence_count",
            "paragraph_count",
            "unique_word_count",
            "reading_time",
        ):
            writer.writerow([key, getattr(document, key)])
        for key in (
            "characters_without_spaces",
            "average_word_length",
            "average_sentence_length",
            "lexical_diversity",
        ):
            writer.writerow([key, getattr(document.analysis, key)])
        writer.writerow([])
        writer.writerow(["Keyword", "Frequency"])
        for keyword in document.analysis.keywords:
            writer.writerow([keyword["word"], keyword["count"]])
        content, mimetype, filename = (
            output.getvalue(),
            "text/csv; charset=utf-8",
            f"{stem}_analysis.csv",
        )
    else:
        from flask import abort

        abort(404)
    return send_file(
        BytesIO(content.encode("utf-8")),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename,
    )


@bp.post("/documents/<int:document_id>/delete")
@login_required
def delete(document_id):
    document = document_for_user(document_id)
    delete_document(document)
    flash("Document and its analysis were deleted.", "success")
    return redirect(
        url_for(
            "admin.documents"
            if current_user.is_admin and request.form.get("return_to") == "admin"
            else "documents.index"
        )
    )
