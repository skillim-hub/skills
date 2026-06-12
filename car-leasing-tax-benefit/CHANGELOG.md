# Changelog

All notable changes to this skill are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.



## [2.2.0] - 01/06/2026

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, and status tags.
- Added `price_ceiling_ils` to each tax-year rule.
- Added calculation trace fields for `price_ceiling_ils` and `capped_price_ils`.

### Changed

- Updated 2026 values to rate 2.48%, ceiling ₪596,860, hybrid reduction ₪580, plug-in hybrid reduction ₪1,150, and electric reduction ₪1,380.
- Updated 2025 values to ceiling ₪583,100, hybrid reduction ₪560, plug-in hybrid reduction ₪1,130, and electric reduction ₪1,350.
- Updated 2024 values to ceiling ₪563,790, hybrid reduction ₪540, plug-in hybrid reduction ₪1,090, and electric reduction ₪1,310.
- Updated the formula to apply the tax-year coordinated-price ceiling before the linear 2.48% calculation.
- Updated documentation examples, Hebrew terminology, and test expectations.

### Fixed

- Corrected stale 2026 green-vehicle reductions carried from earlier tables.
- Corrected missing coordinated-price ceiling behavior.
- Corrected 2024 and 2025 historical table values used by tests and examples.

## [2.1.0] - 01/06/2026

### Added

- Added deep neutrality audit report under `references/branding-audit.md`.
- Added Hebrew QA log under `references/hebrew-qa-log.md`.
- Added installable package module `car_leasing_tax_benefit`.
- Added create-then-calculate local request workflow with request identifiers.
- Added environment-aware examples supporting `--env sandbox|production`.

### Changed

- Replaced hyphenated script implementation with underscored script wrappers.
- Updated README installation to `pip install -e .` and development dependency installation.
- Updated development requirements to include `pytest-asyncio`.
- Updated documentation date localization to `DD/MM/YYYY`.
- Updated metadata version to 2.1.0.

### Fixed

- Removed generated caches from the bundled package.
- Removed visual identity wording and public Markdown emoji risk.
- Updated tests to import the installable package directly.

## [2.0.0] - 01-06-2026

### Added

- Comprehensive English `SKILL.md` with examples, edge cases, Mermaid decision tree, anti-patterns, troubleshooting snapshot, and production checklist.
- Full Hebrew `SKILL_HE.md` using Israeli tax, payroll, and accounting terminology.
- Local JSON rule table for Shovi Rechev tax years and vehicle categories.
- Typed synchronous and asynchronous Python client.
- Argparse CLI in the client helper.
- Typer-first CLI wrapper with fallback behavior.
- Batch JSON processing and UTF-8-SIG CSV export.
- API/regulatory reference for non-API usage.
- Workflow guide with end-to-end operational processes.
- Troubleshooting guide.
- Test-scenarios reference with 30 scenarios.
- Migration checklist for spreadsheet/manual-process adoption.
- Runnable examples under `scripts/examples/`.
- Pytest suite with 30 tests.
- `pyproject.toml`, `requirements-dev.txt`, `README.md`, and MIT license.

### Changed

- Removed all branding, visual identity references, distribution notes, and creator metadata.
- Reframed documentation in a neutral imperative voice.
- Expanded metadata tags and bumped version.

### Security

- Added explicit validation for unsupported categories, invalid tax rates, invalid months, and malformed rule tables.

## [1.0.0] - 01-01-2025

### Added

- Initial skill package baseline.
