from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField


class UploadForm(FlaskForm):
    pdf = FileField(
        "PDF document",
        validators=[FileRequired(), FileAllowed(["pdf"], "Please choose a PDF file.")],
    )
    submit = SubmitField("Extract & analyze")
