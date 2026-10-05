# Verification record

Verified locally on 2026-10-05 with Python 3.12.14 and SQLite.

- `python -m pytest -q`: **44 passed**. One upstream Flask-Login deprecation warning concerns its internal `datetime.utcnow()` use in remember-cookie expiry.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 31 Python files formatted.
- `python -m pip check`: no broken requirements.
- `flask --app run db upgrade`: initial migration applied successfully.
- `flask --app run db check`: no pending schema changes.
- `python seed.py`, repeated: two accounts, five documents and five analysis records; second seed added zero documents.
- `python run.py`: started successfully on localhost with debug disabled.
- Six actual Chromium captures saved under `screenshots/`, using a 1440 × 900 viewport. Dashboard, analysis and admin images include full-page content.
- Browser checks passed for demo/admin login, filename filtering, PDF upload, real extraction/analysis, chart rendering, case-insensitive search/highlights, TXT download content, confirmed deletion, user denial at `/admin`, dark-theme persistence and 390-pixel mobile layouts/navigation.
- All ten pages of the five original sample PDFs were rendered and visually inspected.
- Git ignore checks confirmed exclusions for `.env`, `instance/app.db`, runtime uploads, the virtual environment, pytest/Ruff caches and temporary browser files.

The environment blocked loopback sockets between processes. The browser checks used the documented Flask stdio bridge, which returns actual application responses and invokes real database/services; HTML, statistics and charts are not mocked. The normal application entry point remains a standard Flask/WSGI server. PostgreSQL and the configured Python 3.11 CI job were not executed locally.
