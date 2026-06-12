# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-01

### Added

- Added `references/verification-log.md` with two-pass web validation for Israeli VAT, Section 102, capital-gains rates, surtax, income tax brackets, National Insurance, health contributions, official forms, and API non-applicability.
- Added a web-validated source map to `references/api-reference.md`.
- Added explicit 2026 constant-set sections to English and Hebrew guides.
- Added tests for 2026 employee-side National Insurance and health contribution rates.

### Changed

- Bumped package metadata to version 2.2.0.
- Clarified that VAT is business context only and is not applied to employee-equity tax calculations.
- Expanded the official-source refresh workflow for production use.

### Fixed

- Corrected employee-side National Insurance plus health contribution defaults from 3.50% and 12.00% to 4.27% and 12.17% after Pass 2 validation against National Insurance sources.

## [2.1.0] - 2026-06-01

### Added

- Added installable `stock_options_tax_advisor` package so `from stock_options_tax_advisor import ...` works after `pip install -e .`.
- Added branding audit report and Hebrew quality-assurance log.
- Added environment-aware examples that accept `--env sandbox|production` and print localized JSON.

### Changed

- Replaced hyphenated client filename with underscored client compatibility file.
- Updated README install flow to use editable install and development requirements.
- Updated quick start to create a scenario and pass the returned object into the next calculation step.
- Removed public Markdown emoji, decorative image references, and provenance phrasing.

### Fixed

- Removed file-loading import hacks from CLI and tests.
- Confirmed syntax with `python -m compileall scripts/ -q`.

## [2.0.0] - 2026-06-01

### Added

- Added bilingual English and Hebrew skill guides.
- Added references for regulations, workflows, troubleshooting, test scenarios, and migration.
- Added local client, CLI, examples, tests, project metadata, and MIT license.
