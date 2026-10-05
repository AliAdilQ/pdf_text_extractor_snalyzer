"""Fetch pinned frontend assets. Already vendored; only needed to refresh them."""

from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "fonts/dm-sans.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf",
    "fonts/manrope.ttf": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/manrope/Manrope%5Bwght%5D.ttf",
    "DM-SANS-LICENSE.txt": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/dmsans/OFL.txt",
    "MANROPE-LICENSE.txt": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/manrope/OFL.txt",
    "bootstrap.min.css": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
    "bootstrap-icons.css": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css",
    "fonts/bootstrap-icons.woff2": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff2",
    "fonts/bootstrap-icons.woff": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/fonts/bootstrap-icons.woff",
    "chart.umd.js": "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.js",
    "BOOTSTRAP-LICENSE.txt": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/LICENSE",
    "BOOTSTRAP-ICONS-LICENSE.txt": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/LICENSE",
    "CHARTJS-LICENSE.txt": "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/LICENSE.md",
}

if __name__ == "__main__":
    for filename, url in ASSETS.items():
        destination = ROOT / "app/static/vendor" / filename
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(url, timeout=45) as response:
            destination.write_bytes(response.read())
        print(f"Saved {filename}")
