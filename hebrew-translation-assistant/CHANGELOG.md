# Changelog

All notable changes to this skill package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.

## [2.2.0] - 2026-06-03

### Added

- Web verification log with two-pass validation for Israeli VAT, Israel Invoices thresholds, API paths, withholding tax, consumer cancellation, privacy, accessibility, and official terminology.
- Source-sensitive reference facts command: `hebrew-translation-assistant facts`.
- Release facts for 18% VAT from 01/01/2025 and Israel Invoices 5,000 ₪ threshold from 01/06/2026.
- API reference tables for reference-only Israel Invoices endpoints and API errors.

### Changed

- Changed public descriptions from guarantee-style translation wording to assistant and review wording.
- Updated official-source guidance to state that government API paths are reference-only and the helper does not call them.
- Updated tests for source-sensitive reference facts and CLI `facts` output.

### Verified

- Pass 1 confirmed the VAT rate through official Tax Authority terminology and Israel Invoices thresholds through Tax Authority service pages.
- Pass 2 confirmed the 2026 Israel Invoices 5,000 ₪ threshold through a separate Tax Authority announcement and English topic page.
- Pass 2 confirmed VAT change history through a separate Knesset announcement and Tax Authority history page.
- API host and path references were checked against official Tax Authority API PDFs and a separate mirror of the same Tax Authority documentation.
- Consumer cancellation, privacy, accessibility, and withholding-tax terminology were double-checked against separate official pages.

### Corrected

- Replaced any possible reliance on the older 2025 Israel Invoices threshold with the 03/06/2026 release reference: 5,000 ₪ before VAT from 01/06/2026.

## [2.1.0] - 2026-06-03

### Added

- Installable `hebrew_translation_assistant` Python module with public imports.
- Stored request workflow for CLI create and show commands.
- Environment-aware examples that accept `--env sandbox|production` and read environment variables.
- Branding audit report under `references/branding-audit.md`.
- Hebrew quality assurance log under `references/hebrew-qa-log.md`.

### Changed

- Moved implementation out of hyphenated script filenames into import-safe module files.
- Updated date localization to Israeli `DD/MM/YYYY` format across documentation, tests, and helper code.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to extract an id from a create response and use it in the next command.
- Expanded tests for package importability, CLI chaining, async methods, storage, validation, and date handling.

### Removed

- Hyphenated Python client and CLI implementation files.
- Script-local import loading and path modification patterns.
- Public Markdown emoji, visual branding references, and visual branding references.

## [2.0.0] - 2026-06-03

### Added

- Neutral `hebrew-translation-assistant` package structure.
- Comprehensive English `SKILL.md` for Hebrew-English translation in Israeli small-business, freelance, and consumer contexts.
- Full Hebrew `SKILL_HE.md` using natural Israeli professional terminology, `₪`, and localized date examples.
- `references/api-reference.md` with official-source checklist, helper API reference, request and response examples, and error tables.
- `references/workflow-guide.md` with end-to-end workflows.
- `references/troubleshooting.md` with detailed remediation guidance.
- `references/test-scenarios.md` with more than 20 concrete scenarios.
- `references/migration-checklist.md` for migration from generic translation and older localization material.
- Typed sync and async Python helper.
- Typer CLI.
- Pytest suite with more than 20 tests.
- Runnable scenario examples under `scripts/examples/`.
- `README.md`, `LICENSE`, `pyproject.toml`, and `requirements-dev.txt`.

### Changed

- Refocused scope from generic Hebrew internationalization to practical Hebrew-English translation assistance.
- Expanded terminology coverage for Israeli invoices, receipts, VAT, refunds, delivery, privacy, accessibility, and consumer support.
- Added explicit register handling for formal, business, casual, support, legal-sensitive, and accounting-sensitive output.
- Added idiom handling for common Israeli expressions.

### Removed

- Organization-specific naming.
- Visual branding assets and image references.
- Ownership metadata fields.
