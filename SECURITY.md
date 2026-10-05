# Security

PDF Text Extractor & Analyzer is a Portfolio / Educational Project. Security improvements are welcome.

## Safe configuration

- Never commit or publish production secret keys, `.env`, database credentials, or private user documents.
- Set a unique random `SECRET_KEY` for each deployment. Rotate compromised secrets; existing sessions will need to sign in again.
- The seeded `admin` and `demo` accounts use publicly documented passwords. **Change or remove both before any public deployment.** Do not seed demo data in production.
- Use HTTPS, secure cookies, a maintained WSGI server and dependencies, appropriate login rate limiting, and regular backups for public hosting.

## Untrusted uploads

Uploaded PDFs are untrusted. Extension, MIME, signature, size, page-count and text-length checks reduce accidental misuse but are not a malware scanner or a complete parser sandbox. For public hosting, isolate processing in constrained workers with time and memory limits and consider a scanning service. Uploads must remain outside publicly executable or static directories. Do not serve raw uploaded PDFs without deliberate access controls.

All document reads, exports and deletion routes enforce ownership or administrator access. State-changing forms use CSRF protection. User content is escaped in templates and highlights use safe DOM nodes.

## Responsible reporting

Use the repository's **private vulnerability reporting** feature on [GitHub Security](https://github.com/AliAdilQ/pdf_text_extractor_snalyzer/security) when available. If private reporting is not enabled, open an issue requesting a private reporting channel **without publishing exploit details or sensitive data**. Do not invent contact addresses or disclose another person's files.

Include affected versions, a minimal reproduction using synthetic data, the impact, and any suggested fix. Give maintainers reasonable time to investigate and resolve the issue before public disclosure. There is no guaranteed response SLA.
