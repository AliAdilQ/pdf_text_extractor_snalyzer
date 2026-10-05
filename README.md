# PDF Text Extractor & Analyzer

A modern Flask web application for extracting, analyzing, and exploring text from PDF documents.

Developed as a portfolio project demonstrating Python, Flask, NLP, database management, authentication, data visualization, and modern web development.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-222222?logo=flask)
![License: MIT](https://img.shields.io/badge/License-MIT-6855d9)
![Status: Portfolio / Educational Project](https://img.shields.io/badge/Status-Portfolio%20%2F%20Educational-268d79)

**Extract. Analyze. Understand Your PDFs.** A private document workspace with a polished dashboard, transparent text statistics, useful exports, and a custom administration panel.

[Repository](https://github.com/AliAdilQ/pdf_text_extractor_snalyzer) · [Author](https://github.com/AliAdilQ) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

## Features

- **Secure accounts:** registration, hashed passwords, username/email login, remember me, profile editing, password changes, and POST-only logout.
- **PDF uploads:** drag and drop, selected-file preview, processing feedback, configurable 10 MB request limit, MIME/extension/signature checks, and random storage filenames.
- **Reliable extraction:** pypdf with a pdfplumber fallback; page-by-page text; clear handling of corrupt, encrypted, empty, and image-only PDFs.
- **Text analysis:** words, unique words, characters, characters without whitespace, sentences, paragraphs, reading time, average lengths, and lexical diversity.
- **Keyword discovery:** top 20 keywords with English stopwords removed, most common words, longest words, and shortest meaningful words.
- **Visual exploration:** responsive Chart.js top-10 keyword bar chart and tabs for overview, extracted text, keywords, statistics, and document information.
- **Search:** literal, case-insensitive text search with occurrence counts, up to 30 context snippets, and highlights throughout page text.
- **Document library:** owner-scoped history, filename search, status filters, sorting, pagination, quick view, and confirmed deletion.
- **Exports:** cleanly named TXT text files and CSV analysis reports.
- **Custom administration:** application-wide metrics, user search and account management, role changes, activation/deactivation, safe deletion, all documents, and analysis records.
- **Thoughtful interface:** responsive navigation, accessible form labels and keyboard tabs, empty states, styled errors, flash messages, and persistent light/dark themes.
- **Original demo content:** five real educational PDFs and idempotent seeding; all demo statistics come from the extraction pipeline.

## Screenshots

Real screenshots of the running application, captured at a 1440 × 900 desktop viewport with the included demo data.

### Home Page

![Home Page](screenshots/home.png)

### Login

![Login](screenshots/login.png)

### User Dashboard

![Dashboard](screenshots/dashboard.png)

### PDF Upload

![PDF Upload](screenshots/upload.png)

### Analysis Results

![Analysis Results](screenshots/analysis.png)

### Admin Dashboard

![Admin Dashboard](screenshots/admin-dashboard.png)

See [screenshot capture instructions](screenshots/README.md) to reproduce these images and run the browser verification workflow.

## Demo Credentials

Run the demo seed command before signing in with these accounts.

| Account | Username | Email | Password |
| --- | --- | --- | --- |
| Administrator | `admin` | `admin@example.com` | `Admin123!` |
| Demo user | `demo` | `demo@example.com` | `Demo123!` |

**These credentials are intended only for local demonstration. Change or remove them before production deployment.** Demo seeding is disabled when `APP_ENV=production`. Credentials are confined to the explicit seed utility; authentication always verifies stored password hashes.

The demo user owns the five sample documents. The administrator can review them through `/admin/documents`. An administrator's personal dashboard shows only their own uploads, just like every other account.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Backend | Python 3.11+, Flask, Werkzeug, python-dotenv |
| Accounts and forms | Flask-Login, Flask-WTF, email-validator |
| Persistence | Flask-SQLAlchemy, SQLite, Flask-Migrate / Alembic |
| PDF processing | pypdf, pdfplumber |
| Text processing | NLTK tokenization and stopwords with an offline fallback |
| Frontend | Jinja2, HTML5, custom CSS, Bootstrap 5, Bootstrap Icons, JavaScript |
| Visualization | Chart.js |
| Demo PDFs | ReportLab |
| Verification | pytest; optional Playwright browser checks |
| WSGI serving | Waitress |

Bootstrap, Bootstrap Icons, Chart.js, DM Sans, and Manrope are vendored locally with their license notices. Typography also includes system-font fallbacks. No network or frontend build is required to render the Flask application after installation.

## Project Architecture

```text
pdf_text_extractor_snalyzer/
├── app/
│   ├── __init__.py              # Factory, extensions, security headers, errors
│   ├── extensions.py
│   ├── models.py                # User → Document → Analysis
│   ├── cli.py                   # Explicit, idempotent local demo seeding
│   ├── auth/                   # Authentication and profile forms/routes
│   ├── main/                   # Public home and private dashboard
│   ├── documents/              # Upload, history, services, search and exports
│   ├── admin/                  # Custom, role-protected management panel
│   ├── utils/                  # Extraction, statistics and authorization
│   ├── templates/              # Jinja pages, macros and shared table
│   └── static/                 # CSS, JavaScript, SVG brand and vendor assets
├── migrations/                 # Checked-in initial Alembic migration
├── sample_data/                # Original content and five small sample PDFs
├── screenshots/                # Six real screenshots and capture instructions
├── docs/                       # Social preview and generation notes
├── tools/                      # Sample generation, assets and browser checks
├── tests/                      # Authentication, PDF, ownership and admin tests
├── uploads/.gitkeep            # Runtime uploads are ignored by Git
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── config.py
├── run.py
├── seed.py
├── requirements.txt
├── package.json                # Optional screenshot tooling only
├── pytest.ini
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── SECURITY.md
```

The application factory supports test configuration overrides. Routes coordinate requests, services handle ingestion and cleanup, and extraction/statistics are independent of request handling. Each document has a one-to-one analysis record. Page text is stored once in JSON; `Document.extracted_text` assembles a full view without duplicating the text in the database. Deleting a document cascades to its analysis. Deleting a user cascades to their documents and analyses, and removes uploaded files.

## Installation

### 1. Clone and create a virtual environment

Install **Python 3.11 or newer**, then:

```bash
git clone https://github.com/AliAdilQ/pdf_text_extractor_snalyzer.git
cd pdf_text_extractor_snalyzer
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source venv/bin/activate
```

If Windows PowerShell restricts activation scripts, use Command Prompt or run commands with `venv\Scripts\python.exe` directly. Confirm that `python --version` reports at least 3.11.

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Set up the environment

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Generate a random secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Set the generated value as `SECRET_KEY` in `.env`. This is a machine-specific secret and must not be committed. The included `.env.example` documents every supported setting.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | None | Session and CSRF signing; use a unique random value |
| `DATABASE_URL` | `sqlite:///app.db` | SQLite database in `instance/`, or a SQLAlchemy database URL |
| `MAX_CONTENT_LENGTH` | `10485760` | Maximum HTTP request size in bytes, including multipart overhead |
| `MAX_PDF_PAGES` | `300` | Maximum pages allowed per PDF |
| `MAX_EXTRACTED_CHARACTERS` | `2000000` | Extracted text processing limit |
| `APP_ENV` | `development` | Set to `production` for secure cookies and enforced secret configuration |
| `FLASK_APP` | `run:app` | Flask CLI entry point |

If no secret is supplied in development, the application creates an ephemeral one and logs a warning. Sessions will not persist across restarts in that case. Production startup rejects a missing secret or the example placeholder. The application never enables debug mode automatically.

### 4. Initialize the database

```bash
python -m flask --app run db upgrade
```

The checked-in migration creates all tables. You do **not** need to run `db init` or `db migrate` to install the project.

### 5. Add demo data

```bash
python seed.py
```

Equivalent CLI command:

```bash
python -m flask --app run seed-demo
```

Run it twice safely: existing demo accounts, passwords and sample records are preserved. Missing sample documents are added. Five original two-page PDFs are included under `sample_data/`; they can also be regenerated with `python tools/generate_samples.py`. No copyrighted books or articles are downloaded.

### 6. Run the application

```bash
python run.py
```

Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)**. Stop the server with Ctrl+C.

For a local WSGI server:

```bash
waitress-serve --listen=127.0.0.1:5000 run:app
```

Keep `APP_ENV=development` for plain HTTP on localhost. When using production secure cookies, serve the application behind HTTPS.

## Application Usage

1. Register an account or sign in as `demo`.
2. Open **Upload PDF**, drag in a document or browse for it, and choose **Extract & analyze**.
3. Review the overview, keyword chart, and preview. Switch to **Extracted text** for the full page-by-page content.
4. Search a word or phrase to see occurrence counts, context snippets, and highlighted matches.
5. Explore **Keywords**, **Statistics**, and **Document info** for detailed metrics and metadata.
6. Download **Export text** as TXT, or use **Export CSV** in the statistics tab.
7. Return to **My documents** to search filenames, filter status, sort, page through history, and delete files.
8. Use **Account settings** to change your email or password, and the header theme button to switch appearance.

Text search counts literal substrings, case-insensitively. All textual content is escaped when rendered; highlights are constructed with safe DOM nodes. Counts are calculated from alphabetic tokens, including apostrophe contractions. Sentence detection uses punctuation boundaries and may overcount abbreviations. Paragraphs are separated by blank lines; PDF extraction may not preserve the original paragraph structure. Reading time assumes 200 words per minute. English stopwords are loaded from NLTK when available, with a bundled fallback requiring no resource download.

## Admin Panel

Sign in as `admin` and visit **[/admin](http://127.0.0.1:5000/admin)**.

- **Overview:** total users, PDFs, pages and words; recent uploads and accounts.
- **Manage users:** search accounts, view a user's uploads, change role, activate/deactivate, or delete an account and its associated files.
- **All documents:** search by filename or owner, view metadata/analysis, export text, and delete documents.
- **Analysis records:** inspect stored keyword counts, lexical diversity and average word lengths; open the associated document for full detail.

Every admin route enforces authorization on the server. Normal users receive a styled 403 page. Administrators cannot deactivate, demote or delete their own account. A safety check preserves an active administrator. Deactivated accounts lose access on their next request, including previously remembered sessions. Analysis records are managed through their parent document to preserve consistency.

## Running Tests

```bash
pytest
```

Or `python -m pytest -q`. Tests use an isolated in-memory SQLite database and temporary upload directories; the demo database and uploaded user files are not touched. Workspace-local temporary files are written under ignored `tmp/pytest/` for compatibility with restricted environments.

For the optional Python style checks, install `python -m pip install -r requirements-dev.txt`, then run `ruff check .` and `ruff format --check .`.

Coverage includes registration, duplicate identities, login/logout, remember-me cookies, password changes, CSRF enforcement, inactive accounts, protected routes, admin access, cross-account document reads/exports/deletes, user deletion cascades, PDF extension/MIME/signature validation, corrupt/encrypted/zero-page/no-text PDFs, size/page/text limits, statistics, Unicode, literal search, TXT/CSV exports, and filesystem cleanup.

The included GitHub Actions workflow runs tests on Python 3.11 and 3.12 and exercises migrations and demo seeding.

### Optional browser checks and screenshots

With Node.js installed and the Flask server running:

```bash
npm install
npx playwright install chromium
npm run screenshots
```

This captures the six README screenshots and checks real login, upload, extraction, charts, search, export, deletion, authorization, theme persistence, and mobile layout. It temporarily adds and deletes one test upload in the local demo account. See [screenshots/README.md](screenshots/README.md) for details.

## Security and Deployment Notes

- Passwords are hashed with Werkzeug. Forms, uploads, account management and deletion use CSRF protection.
- Every document read, search, export and deletion checks ownership or administrator status.
- Only sanitized display filenames and random UUID storage filenames are used. Uploads are outside public static assets and are never served as executable content.
- MIME and PDF signature checks supplement extension validation. PDF parsing has page and extracted-character limits, but uploaded documents remain untrusted input.
- `.env`, databases, caches, virtual environments, and runtime uploads are ignored. Original `sample_data/` PDFs are safe to commit. Do not commit real user documents.
- Request limits include multipart overhead, so a PDF exactly at the configured limit may need to be slightly smaller.
- For public hosting, change/remove demo accounts, use a strong secret, HTTPS, a WSGI server, backups, trusted reverse-proxy configuration, login rate limiting, and isolated workers with processing time/memory limits.
- PDF processing is synchronous and intended for reasonably sized documents. This **Portfolio / Educational Project** does not claim enterprise readiness.
- OCR is not included. Image-only PDFs are retained with an explanatory warning and zero text statistics. Encrypted PDFs are rejected; upload an unprotected copy.

Read [SECURITY.md](SECURITY.md) for responsible reporting guidance.

### PostgreSQL

Models and migrations use SQLAlchemy. To switch a fresh installation to PostgreSQL, install its optional driver:

```bash
python -m pip install "psycopg[binary]"
```

Set `DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/DATABASE` in your private `.env`, then run `python -m flask --app run db upgrade`. This creates a new schema; it does not transfer existing SQLite data. SQLite is the default tested configuration. PostgreSQL is a deployment option and needs its own integration validation.

## GitHub Social Preview

![GitHub Social Preview](docs/github-social-preview.png)

The optional social image is saved at `docs/github-social-preview.png`. Use the compact `docs/github-social-preview.jpg` export when uploading through GitHub's social preview settings. [Generation notes](docs/social-preview.md) record the prompt and built-in image-generation method. All core UI illustrations are original CSS/SVG compositions.

## Future Improvements

- OCR for scanned PDFs and multilingual tokenization.
- Multiple-document and PDF-to-PDF comparison.
- AI-generated summaries with source references.
- Named entity recognition and topic modeling.
- Background processing with progress updates and stronger resource isolation.
- Cloud storage and validated PostgreSQL deployment.
- A versioned REST API.

## Contributing

Contributions are welcome. Fork the repository, create a focused branch, add tests for meaningful behavior, and open a pull request. Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Released under the [MIT License](LICENSE). Vendored libraries retain their respective MIT notices in `app/static/vendor/`.
DM Sans and Manrope retain their SIL Open Font License notices in the same directory.

## Author

Built by **[AliAdilQ](https://github.com/AliAdilQ)**.

Repository: **[AliAdilQ/pdf_text_extractor_snalyzer](https://github.com/AliAdilQ/pdf_text_extractor_snalyzer)**.
