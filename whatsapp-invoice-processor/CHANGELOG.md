# Changelog

All notable changes to this package are documented in this file. The format follows Keep a Changelog, and versioning follows semantic versioning.

## [0.4.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation rows, source snippets, URLs, and access date.
- Added effective-date allocation threshold helper for 2024, 2025, January-May 2026, and June 2026 onward.
- Added tests for the accelerated 2026 allocation thresholds and production environment defaults.

### Changed

- Updated Invoice Israel allocation threshold guidance from the older 2026 ₪15,000 schedule to the current accelerated schedule: ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026.
- Updated public examples and references to use `DD/MM/YYYY` display dates consistently.
- Expanded API reference with live validation notes for VAT, allocation numbers, WhatsApp media/webhooks, and privacy sources.

### Fixed

- Corrected stale threshold values in `references/api-reference.md`, client defaults, examples, and tests.
- Clarified that OCR extraction is local workflow behavior while WhatsApp media and messaging primitives are verified through official Meta documentation.

## [0.3.0] - 2026-06-03

### Added

- Added installable `whatsapp_invoice_processor` package modules for direct imports without path manipulation.
- Added `references/branding-audit.md` and `references/hebrew-qa-log.md`.
- Added public command entry point through `pyproject.toml`.
- Added environment-aware examples with `--env sandbox|production` and JSON output using `ensure_ascii=False`.

### Changed

- Replaced the hyphenated client implementation file with an underscored compatibility import and installable package implementation.
- Updated Hebrew display dates to `DD/MM/YYYY` and expanded Israeli terminology checks.
- Updated README installation and quick-start flow to use `pip install -e .` and chained response identifiers.
- Expanded development requirements with `pytest-asyncio`.

### Fixed

- Removed generated cache files and the duplicated hyphenated test artifact from the distributed archive.
- Removed public Markdown emoji and any badge URLs or decorative image references.
- Kept only the required neutral license attribution.

## [0.2.0] - 2026-06-03

### Added

- Added English and Hebrew guides, references, CLI, tests, examples, metadata, and license.

## [0.1.0] - 2026-06-03

### Added

- Initial skill package scaffold.
