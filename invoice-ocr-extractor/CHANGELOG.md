# Changelog

The format follows Keep a Changelog and semantic versioning.


## [2.2.0] - 2026-06-01

### Added

- Two-pass web verification log with official and secondary sources for VAT rate, allocation thresholds, Tax Authority endpoint paths, privacy, recordkeeping, and terminology.
- Allocation-threshold helper functions for 2025 and 2026 date ranges.
- Review flag for ILS tax invoices above the verified allocation threshold when no allocation number is visible.
- Tests for 2026 allocation thresholds and missing/present allocation-number handling.

### Changed

- Corrected stale 2026 allocation-threshold guidance from the older 07/2024 API table to the current phase-down schedule: ₪10,000 before VAT from 01/01/2026 and ₪5,000 before VAT from 01/06/2026.
- Bumped schema and package metadata to 2.2.0.
- Expanded API reference with current Tax Authority endpoint paths, hosts, OAuth2 notes, and no-webhook clarification.
- Updated Hebrew documentation with web-validated terminology and neutral review wording.

### Verified

- VAT rate 18% was double-confirmed against official VAT history and a 2026 tax summary.
- Allocation-number thresholds were corrected in pass 2 using the current Tax Authority service page.
- Allocation request fields, no-fee status, OAuth2, privacy, corporation lookup, and scanning/archive guidance were double-confirmed.

## [2.1.0] - 2026-06-01

### Added

- Branding and authorship audit report.
- Hebrew QA log.
- Installable `invoice_ocr_extractor` package under `src/`.
- Record id generation for create-response chaining.
- CLI validation option for expected record id.
- Example scripts that read environment variables and accept `--env sandbox|production`.

### Changed

- Replaced hyphenated script module names with underscored script names.
- Updated README installation commands to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated date localization in public documentation to `DD/MM/YYYY`.
- Updated tests to import the installable package without path hacks.

### Removed

- Hyphenated client and CLI script filenames.

## [2.0.0] - 2026-06-01

### Added

- Comprehensive English and Hebrew skill guides.
- Israeli API/regulation reference with request/response examples and error tables.
- Workflow, troubleshooting, test-scenario, and migration references.
- Typed sync and async Python client.
- Click-based CLI with parse, batch, validate, and schema commands.
- Pytest suite with more than 20 tests.
- Five runnable examples.
- MIT license.
- Packaging and development files.

### Changed

- Expanded schema with confidence, review flags, evidence snippets, business ID type, allocation number, and schema version.
- Improved VAT extraction, exempt dealer handling, credit-note handling, and document-number exclusions.

### Removed

- Non-neutral names, decorative media, creator fields, and promotional callouts.
