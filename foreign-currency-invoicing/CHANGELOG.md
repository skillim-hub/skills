# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and the package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, snippets, access date, statuses, and summary counts.
- Added Bank of Israel SDMX CSV parsing and a date-specific SDMX rate URL builder.
- Added a current-rate URL helper for the Bank of Israel public API.
- Added tests for SDMX CSV parsing and SDMX URL generation.

### Changed

- Changed the default dated Bank of Israel lookup from an unconfirmed `asOfDate` public-API pattern to the official SDMX `RER_<CURRENCY>_ILS` series URL with `startPeriod`, `endPeriod`, and `format=csv`.
- Updated `SKILL.md`, `SKILL_HE.md`, `README.md`, `references/api-reference.md`, `references/workflow-guide.md`, and `references/troubleshooting.md` to reflect the verified endpoint strategy.
- Confirmed the 18% standard VAT default from 01/01/2025 through a second-pass 2026 source and retained the 17% pre-2025 split.
- Confirmed that zero-rate and exempt treatments remain distinct and that foreign-currency denomination alone is not a VAT classification test.

### Fixed

- Corrected malformed code fences in the English guide.
- Removed the unverified date-specific `asOfDate` claim from the API reference.

## [2.1.0] - 2026-06-02

### Added

- Added branding and attribution audit report.
- Added Hebrew quality assurance log.
- Added installable underscored Python modules for client and CLI usage.
- Added CLI create/show chain with generated invoice identifiers and local JSON storage.
- Added additional runnable example for CLI chaining.

### Changed

- Replaced hyphenated client module with an underscored importable module.
- Updated README installation to use editable install plus development requirements.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and indentation.
- Localized Hebrew date guidance to DD/MM/YYYY and shekel display with ₪.
- Expanded tests to cover CLI chaining, asynchronous rate fetching, fallback lookup, and persistence.

### Fixed

- Fixed package installation so `from foreign_currency_invoicing_client import ...` works after `pip install -e .`.
- Removed public Markdown emoji, visual identity references, and residual attribution patterns.

## [2.0.0] - 2026-06-01

### Added

- Added bilingual English and Hebrew guides.
- Added Bank of Israel representative-rate parsing for JSON and XML.
- Added VAT categories and invoice calculation helper.
- Added reference guides, examples, tests, pyproject configuration, and MIT license.
