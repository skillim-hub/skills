# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Web validation log with pass-1 and pass-2 sources, quotes, URLs, access date, and final status tags.
- Double-confirmed 18% Israeli VAT default for 2026.
- Reference-only official endpoint notes for `general-information/v2/MinimumAmount` and `Multi-invoices/v2/MultiApproval`.
- Explicit note that official Israel Invoice webhook event names were not confirmed.
- Regression tests for the web-validated default VAT rate and absence of webhook surface area.

### Changed

- Corrected Israel Invoice allocation threshold guidance for 2026 to above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026 where the legal conditions apply.
- Clarified that fractional agorot handling is a local deterministic rounding feature, not an official Tax Authority API feature.
- Bumped package metadata and Python package version to 2.2.0.

### Verification findings

- Pass 1 confirmed the current VAT rate from official Israel Tax Authority sources.
- Pass 2 double-confirmed the VAT rate with 2026 tax reference material.
- Pass 1 found the older API threshold schedule in the July 2024 API document.
- Pass 2 corrected the threshold using the later VAT Implementation Order 01/2025.
- Searches for official webhook event names returned no relevant Israel Invoice API documentation.

## [2.1.0] - 2026-06-02

### Added

- Branding audit report covering forbidden terms, badge and logo references, attribution fields, and public Markdown emoji checks.
- Hebrew quality-assurance log with terminology, date-format, voice, and niqqud review.
- Installable `multi_line_item_aggregator` package for direct imports.
- Package CLI through `python -m multi_line_item_aggregator.cli`.
- Create-and-aggregate quick-start flow that extracts a draft identifier from a create response and uses it in the next step.
- Example scripts that read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.

### Changed

- Replaced hyphenated client implementation with underscored compatibility script and installable package imports.
- Updated README install instructions to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Hebrew documentation to neutral imperative voice, DD/MM/YYYY dates, and professional Israeli terminology.
- Removed generated cache files from the bundle.

### Fixed

- Eliminated dynamic import hacks from tests and examples.
- Confirmed syntax with `python -m compileall scripts/ -q`.
- Confirmed pytest coverage for installable package imports and CLI chaining.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with examples, edge cases, decision tree, troubleshooting summary, anti-patterns, and production checklist.
- Full Hebrew guide with Israeli terminology, ₪ formatting, and DD-MM-YYYY date examples.
- Regulatory/API reference for Israeli invoice-related workflows and non-API calculation mapping.
- End-to-end workflow guide for freelancers, small shops, consumers, metered billing, mixed VAT, credit notes, marketplaces, and spreadsheet migration.
- Dedicated troubleshooting reference.
- Dedicated test-scenarios reference with 30 scenarios.
- Migration checklist for spreadsheets, legacy scripts, and accounting-system previews.
- Typed sync and async Python helper.
- Click-based CLI.
- Pytest suite with more than 20 tests.
- Runnable examples.
- README, MIT license, pyproject, and development requirements.

### Changed

- Reworked the package as a neutral calculation helper.
- Removed branding, logos, badge references, distribution callouts, and author metadata.
- Expanded metadata tags and bumped version.
- Standardized Decimal-based money calculations.
- Added explicit fractional agorot fields.

### Fixed

- Prevented hidden float rounding behavior by parsing numeric values into Decimal.
- Added validation for empty invoices, negative VAT rates, excessive discounts, zero quantities, and negative lines.
- Added deterministic invoice-discount allocation with cent-level reconciliation.

## [1.0.0] - 2025-01-01

### Added

- Initial skill package.
