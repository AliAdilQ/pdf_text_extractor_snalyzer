"""Build five small, original two-page educational PDFs. No network required."""

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]


def generate_samples(destination=None):
    destination = Path(destination or ROOT / "sample_data")
    destination.mkdir(parents=True, exist_ok=True)
    content = json.loads(
        (ROOT / "sample_data/content.json").read_text(encoding="utf-8")
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SampleTitle",
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=33,
            textColor=colors.HexColor("#332866"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SampleSubtitle",
            fontName="Helvetica",
            fontSize=11,
            leading=17,
            textColor=colors.HexColor("#74758a"),
            spaceAfter=30,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SampleHeading",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=20,
            textColor=colors.HexColor("#6855d9"),
            spaceBefore=17,
            spaceAfter=11,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SampleBody",
            fontName="Helvetica",
            fontSize=10.5,
            leading=17,
            textColor=colors.HexColor("#323546"),
            spaceAfter=12,
        )
    )

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#e8e4f3"))
        canvas.line(48, 43, A4[0] - 48, 43)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#74758a"))
        canvas.drawString(
            48, 29, "PDF Analyzer | Original educational sample | AliAdilQ"
        )
        canvas.drawRightString(A4[0] - 48, 29, f"Page {doc.page}")

    paths = []
    for item in content:
        path = destination / f"{item['title']}.pdf"
        story = [
            Paragraph("PDF ANALYZER / SAMPLE LIBRARY", styles["SampleSubtitle"]),
            Paragraph(item["title"], styles["SampleTitle"]),
            Paragraph(item["subtitle"], styles["SampleSubtitle"]),
        ]
        for index, (heading, body) in enumerate(item["sections"]):
            if index == 2:
                story.extend(
                    [
                        PageBreak(),
                        Paragraph(
                            item["title"] + " / continued", styles["SampleSubtitle"]
                        ),
                    ]
                )
            story.append(Paragraph(heading, styles["SampleHeading"]))
            for paragraph in body.split("\n\n"):
                story.append(Paragraph(paragraph, styles["SampleBody"]))
            story.append(Spacer(1, 5))
        SimpleDocTemplate(
            str(path),
            pagesize=A4,
            rightMargin=48,
            leftMargin=48,
            topMargin=45,
            bottomMargin=62,
            title=item["title"],
            author="AliAdilQ",
        ).build(story, onFirstPage=footer, onLaterPages=footer)
        paths.append(path)
    return paths


if __name__ == "__main__":
    for sample in generate_samples():
        print(sample.relative_to(ROOT))
