# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [0.4.0] - 2026-06-02

### Added

- Two-pass web validation log with official Israeli source snippets, URLs, access date, and validation status per row.
- Explicit 2026 validation notes for VAT, Invoice Israel thresholds, Bank of Israel exchange-rate API host, consumer price display, bookkeeping terminology, and missing public webhook event contracts.

### Changed

- Bumped version from `0.3.0` to `0.4.0`.
- Corrected the Bank of Israel exchange-rate example from an invented generic endpoint to the documented SDMX series API host.
- Clarified that Invoice Israel request and response examples are neutral connector shapes, not official stable endpoint contracts.
- Added Invoice Israel threshold schedule for 2025 and 2026.
- Clarified that no official public webhook event-name contract was confirmed for this catalog use case.

### Verified

- Standard Israeli VAT rate remains represented as `0.18` for 2026 checks.
- Invoice Israel thresholds were double-checked against Tax Authority material and a second professional source.
- Consumer price-display guidance was checked against Consumer Protection Authority material and enforcement materials.
- Hebrew terms `מס ערך מוסף`, `מע״מ`, `מספר הקצאה`, `ניהול ספרים`, and `פנקסי חשבונות` were checked against official terminology.

## [0.3.0] - 2026-06-02

### Added

- Branding audit report.
- Hebrew QA log.
- Importable underscored client module.
- Importable CLI module and console script.
- CLI create-item workflow that returns a reusable JSON id.
- Example scripts with environment selection and environment variable inputs.

### Changed

- Bumped version from `0.2.0` to `0.3.0`.
- Updated installation instructions to separate editable install from development dependencies.
- Updated examples to emit JSON with `ensure_ascii=False` and indentation.
- Updated public documentation to use `DD/MM/YYYY` localization.

### Removed

- Hyphenated client implementation path that could not be imported as a Python module.

## [0.2.0] - 2026-06-02

### Added

- Comprehensive English skill guide with examples, edge cases, decision trees, troubleshooting, anti-patterns, and production checklist.
- Full Hebrew guide with Israeli terminology, ₪ examples, and `DD/MM/YYYY` localization.
- Israeli API and regulation reference with request/response examples and error tables.
- End-to-end workflow guide.
- Dedicated troubleshooting guide.
- 35 concrete test scenarios.
- Migration checklist for spreadsheets, POS exports, accounting exports, and supplier files.
- Typed sync and async Python catalog helper.
- Typer-based CLI.
- pytest suite with more than 20 tests.
- Runnable example scripts.
- Project metadata, development requirements, README, and MIT license.

### Changed

- Bumped version from `0.1.0` to `0.2.0`.
- Replaced stub content with production-oriented guidance.
- Standardized default currency as ILS while allowing configuration.

### Removed

- Creator metadata.
- Branding and visual branding assets.
