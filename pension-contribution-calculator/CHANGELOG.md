# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning where practical.

## [1.2.0] - 2026-06-01

### Added

- Added two-pass web validation log with source URLs, short source quotes, access date, and summary counts.
- Added explicit non-API, no-webhook, and VAT-out-of-scope statements to the regulation reference.
- Added Bituach Menahalim current-law eligibility warnings for policies opened from 01/09/2023.

### Changed

- Bumped the comprehensive pension fund monthly deposit cap from ₪5,645.00 to ₪5,645.29 after second-pass validation.
- Updated documentation, tests, troubleshooting, evidence, and examples to align with the corrected 2026 ceiling.
- Expanded evidence metadata with concrete validated source URLs.

### Validated

- Confirmed Israeli VAT at 18% from 01/01/2025 as an out-of-scope reference.
- Confirmed 2026 average wage of ₪13,769/month.
- Confirmed self-employed mandatory pension brackets at 4.45% and 12.55%.
- Confirmed employee pension split of 6% employee, 6.5% employer pension, and 6% employer severance.
- Confirmed employee Keren Hishtalmut salary ceiling of ₪15,712/month.
- Confirmed self-employed Keren Hishtalmut caps of ₪13,203/year and ₪20,566/year.
- Confirmed uniform reporting interface names including `ממשק מעסיקים - דיווח שוטף`, `ממשק מעסיקים - דיווח שלילי`, and `EVEMAS`.

## [1.1.1] - 2026-06-01

### Fixed

- Replaced the hyphenated client implementation with a real importable underscored module.
- Updated CLI, tests, examples, metadata, documentation, and package configuration to use direct imports.
- Added calculation record creation and verification flow for chained quick-start usage.
- Added development installation instructions with editable install and async test dependency.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print UTF-8 JSON with two-space indentation.
- Added branding audit and Hebrew quality-assurance logs.

### Removed

- Removed the legacy hyphenated client file.

## [1.1.0] - 2026-06-01

### Added

- Comprehensive English skill guide with examples, decision trees, edge cases, troubleshooting, anti-patterns, and production checklist.
- Hebrew skill guide with natural Israeli professional terminology and ₪ localization.
- Local helper contract and regulation/source registry in `references/api-reference.md`.
- End-to-end operational workflows in `references/workflow-guide.md`.
- Detailed troubleshooting reference.
- Thirty concrete test scenarios.
- Migration checklist for spreadsheets, payroll macros, old calculators, and annual rate updates.
- Typed synchronous and asynchronous Python helper.
- Typer CLI with employee, self-employed, comparison, and rates commands.
- Six runnable example scripts.
- Pytest suite covering core calculations, validation, async helper, rate loading, and examples.
- Project configuration and development requirements.
- MIT license.

### Changed

- Renamed package slug to `pension-contribution-calculator`.
- Expanded metadata tags and entrypoints.
- Reworked calculations around a versioned `RateTable`.

### Removed

- Previous package identifiers and visual references.
- Metadata person or organization attribution.

## [1.0.0] - 2026-05-18

### Added

- Initial pension contribution guide and calculator script.
