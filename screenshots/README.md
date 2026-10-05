# Real application screenshots

The six PNG files are screenshots of the running Flask application at a **1440 × 900** desktop viewport. They are not generated UI mockups. Sample statistics are calculated from the original PDFs in `sample_data/`.

| File | View |
| --- | --- |
| `home.png` | Public landing page |
| `login.png` | Sign-in form |
| `dashboard.png` | Demo user's document overview |
| `upload.png` | Drag-and-drop upload form |
| `analysis.png` | A newly uploaded sample PDF's analysis and Chart.js chart |
| `admin-dashboard.png` | Administrator overview, users and all uploads |

## Reproduce

Initialize and seed the application using the root README. Keep `python run.py` running in one terminal. In another terminal, install optional browser tooling:

```bash
npm install
npx playwright install chromium
npm run screenshots
```

The script signs in with the documented demo accounts, captures all six files, and checks upload, extraction, filename filtering, chart rendering, highlighted search, downloaded TXT content, deletion, admin access control, theme persistence, and mobile layout. It creates and deletes one temporary upload in the local demo account. Run against a local seeded workspace whose public demo passwords have not been changed.

Optional variables:

- `APP_URL`: defaults to `http://127.0.0.1:5000`.
- `BROWSER_EXECUTABLE`: use an existing Chromium-compatible browser executable.
- `BROWSER_CHANNEL`: alternatively use a Playwright channel such as `msedge`.

In environments that block loopback network connections, set `APP_BROWSER_BRIDGE=1` and optionally `PYTHON_EXECUTABLE` to the project's Python executable. This uses `tools/browser_bridge.py` to transport requests through Flask's real test client over stdio. Chromium still renders the actual HTML, CSS and JavaScript, manages cookies, and exercises the real database/services. The supplied screenshots were captured using this transport because this workspace restricted localhost sockets. No screenshot content is mocked.

Additional dark-theme and mobile verification captures go to ignored `tmp/browser/`; exported test text goes there too. Refresh screenshots after significant design changes. Never capture real private documents for repository images.
