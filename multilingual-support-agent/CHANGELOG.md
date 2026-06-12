# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.


## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, short source snippets, status tags, and summary counts.
- Added dated Israeli reference snapshots to the English and Hebrew skill guides.
- Added Israel Tax Authority API host and path references with a warning to verify current developer-portal details before production integration.

### Changed

- Confirmed the standard Israeli VAT context as 18% after the 01/01/2025 increase and retained accounting escalation for VAT classification.
- Confirmed Israel Invoices allocation thresholds: ₪20,000 for 2025, ₪10,000 from 01/01/2026, and ₪5,000 from 01/06/2026, excluding VAT.
- Corrected public language-scope wording from any ranking-style implication to high-coverage customer-service language support.
- Standardized Hebrew professional terminology for מע״מ, מס תשומות, מספר הקצאה, חשבונית מס, ביטול עסקה, דואר אלקטרוני, and תבנית.
- Marked conflicting official PDF path naming for the invoice-decision service as an integration risk that must be reverified before use.

### Verified

- Rechecked consumer protection, privacy, accessibility, marketing/spam, payments, business registry, open-data/API, and language-status references against live sources.
- Re-ran neutral branding, author, decorative visual, and public-Markdown emoji audits.

## [2.1.0] - 2026-06-03

### Changed

- Replaced hyphenated Python script imports with installable package imports and underscore-named script files.
- Added an installable `multilingual_support_agent` package with typed sync and async client methods.
- Updated README installation commands to use editable installation and development requirements.
- Updated quick-start commands to extract a case identifier from the create response and reuse it in a follow-up call.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Added Hebrew quality review log and neutral-branding audit report.
- Increased automated tests and added async test coverage.
- Normalized public Markdown by removing decorative symbols, image references, decorative link patterns, and branding references.

## [2.0.0] - 2026-06-03

### Added

- Added English and Hebrew skill guides.
- Added Israeli workflow, troubleshooting, migration, and test-scenario references.
- Added Python client, CLI helper, example scripts, metadata, license, and development configuration.
