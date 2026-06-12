# Changelog

All notable changes to this skill are documented in this file.

The format is based on Keep a Changelog, and this project follows semantic versioning where practical.

## [0.3.0] - 2026-06-01

### Added

- Two-pass web verification log with official Israeli source snippets and access date.
- Official CBS price-index API paths for CPI lookup and indexation workflows.
- VAT reference noting 18% standard VAT rate effective from 01/01/2025 and still reflected in 2026 budget/revenue materials.
- Explicit warning that the default 25% planning rate excludes high-income surtax and additional capital-income tax where applicable.
- Webhook/API-host status note for the non-API skill.

### Changed

- Corrected CPI reference from a normalized local `/cpi`-style contract to official `api.cbs.gov.il` paths plus an optional normalized internal shape.
- Bumped metadata to version 0.3.0.
- Expanded tests to assert the default-rate surtax warning.

### Web validation findings

- Pass 1 and Pass 2 confirmed Israeli VAT at 18% from 01/01/2025 and no contrary 2026 source was found.
- Pass 1 and Pass 2 confirmed official real-estate taxation terminology: `מס שבח`, `מיסוי מקרקעין`, `דירת מגורים מזכה`, `שומה עצמית`, and `ליניאריות מוטבת`.
- Pass 1 and Pass 2 confirmed official forms/services: 7000, 7000ב, 7002 references, 7003, 7914, 2988, 7157, 7158, and the self-assessment service.
- Pass 1 and Pass 2 confirmed CBS API host `api.cbs.gov.il` and CPI series examples using code `120010`.
- Pass 2 corrected the package to add clearer surtax/additional capital-income-tax caveats for 2025 onward.
- No official webhook event names were identified for this non-API skill.

## [0.2.1] - 2026-06-01

### Added

- Branding and attribution audit report.
- Hebrew quality-assurance log.
- Installable underscored Python module.
- Local case creation and case-based estimation workflow for chained CLI usage.
- Environment-aware runnable examples using environment variables and JSON output.

### Changed

- Replaced hyphenated client implementation with underscored import paths.
- Updated README quick start to create a case, extract the case id, and estimate the saved case.
- Updated tests to import the installable module directly.
- Refined Hebrew localization to use `DD/MM/YYYY` in Hebrew-facing guidance.

### Fixed

- Removed generated cache files from the distributable bundle.
- Confirmed public Markdown contains no emoji, visual marker URLs, visual identity references, or large header images.

## [0.2.0] - 2026-06-01

### Added

- Comprehensive English guide with examples, decision trees, edge cases, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew guide with Israeli professional terminology and localized currency/date presentation.
- Regulation and data reference for Israeli Mas Shevach work.
- End-to-end workflow guide.
- Dedicated troubleshooting guide.
- Test scenario catalog with more than 20 concrete scenarios.
- Migration checklist.
- Typed calculation helper with synchronous and asynchronous APIs.
- Typer CLI with JSON and pretty output modes.
- Runnable example scripts.
- Pytest suite with more than 20 tests.
- README, MIT license, pyproject configuration, and development requirements.

### Changed

- Replaced stub content with production-ready neutral content.
- Expanded metadata tags and bumped version.
- Removed attribution metadata and branding references.

### Fixed

- Added validation for dates, CPI pairs, negative amounts, ownership share, and property type.
- Added warnings for common Israeli real-estate tax risk areas.

## [0.1.0] - Initial

### Added

- Initial stub package.
