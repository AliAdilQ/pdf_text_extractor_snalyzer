"""Render every original sample page for visual quality checks."""

from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
destination = ROOT / "tmp/pdfs"
destination.mkdir(parents=True, exist_ok=True)
paths = sorted((ROOT / "sample_data").glob("*.pdf"))
sheet = Image.new("RGB", (1500, 860), "#e8e7ed")
draw = ImageDraw.Draw(sheet)
for column, path in enumerate(paths):
    with pdfplumber.open(path) as pdf:
        assert len(pdf.pages) == 2, f"Expected two pages in {path.name}"
        for row, page in enumerate(pdf.pages):
            page.to_image(resolution=115).save(
                destination / f"sample-{column + 1}-{row + 1}.png"
            )
            image = page.to_image(resolution=48).original
            image.thumbnail((280, 390))
            sheet.paste(image, (column * 300 + 10, row * 430 + 28))
            draw.text(
                (column * 300 + 10, row * 430 + 8),
                f"Sample {column + 1} / Page {row + 1}",
                fill="#34324e",
            )
sheet.save(destination / "sample-contact-sheet.png")
print("Rendered all ten sample pages into tmp/pdfs/.")
