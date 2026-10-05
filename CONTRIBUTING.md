# Contributing

Thank you for helping improve PDF Text Extractor & Analyzer.

1. Fork [AliAdilQ/pdf_text_extractor_snalyzer](https://github.com/AliAdilQ/pdf_text_extractor_snalyzer).
2. Clone your fork and follow the environment setup in [README.md](README.md).
3. Create a focused branch: `git switch -c feature/clear-description`.
4. Make the change with readable Python, small services, accessible templates, and consistent styling. Add tests for behavior changes and database migrations when the schema changes.
5. Run `pytest`. For interface changes, check desktop/mobile layouts, both themes, empty states, and keyboard navigation. The optional screenshot workflow is documented in `screenshots/README.md`.
6. Commit a clear description of the change: `git commit -m "Describe the behavior improved"`.
7. Push your branch: `git push origin feature/clear-description`.
8. Open a pull request against the upstream default branch. Describe the problem, resulting behavior, and relevant validation. Include screenshots for visual changes.

Keep `.env`, databases, uploads, personal documents, and virtual environments out of commits. Only original or appropriately licensed sample content belongs in `sample_data/`. Preserve third-party license notices.

Report suspected security vulnerabilities using [SECURITY.md](SECURITY.md), rather than a public issue containing exploit details. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
