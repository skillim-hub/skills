# Changelog

All notable changes are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-04

### Added

- Web-validated two-pass verification log with source snippets, URLs, access date, and package actions.
- Official-source boundary explaining that CBS indices update historical costs but do not publish official room renovation rates.
- Verified CBS API host and price-index API references.
- Verified Planning Administration, Rishuy Zamin, Mavat, and permit-fee calculator references.
- Verified business licensing, accessibility, fire-safety, health, waste, asbestos, and standards source references.

### Changed

- Replaced fake endpoint examples with actual official-source links or non-API workflow notes.
- Clarified that per-meter and per-room renovation rates are planning heuristics, not official Israeli rates.
- Kept VAT default at 18% after double confirmation.
- Updated package metadata to version 2.2.0.

### Corrected

- Removed implied official status from renovation benchmark ranges.
- Marked non-CBS API endpoints and webhook names as not applicable.

## [2.1.0] - 2026-06-04

### Added

- Branding and visual-asset audit report.
- Hebrew quality-assurance log.
- Installable Python package with direct imports from `renovation_cost_estimator`.
- Project creation flow with id extraction and follow-up estimate by id.
- Environment-aware CLI and runnable examples.

### Changed

- Moved implementation into an installable package.
- Removed hyphenated client module and obsolete import shims.
- Updated Hebrew localization to DD/MM/YYYY.
- Updated README installation and quick-start flow.

### Fixed

- Eliminated sys.path-style import loading from generated client code.
- Confirmed public Markdown has no emoji, status link URLs, visual visual headers, or visual mark references.

## [2.0.0] - 2026-06-04

### Added

- Comprehensive English guide.
- Full Hebrew guide with Israeli terminology and localization.
- Israeli API and regulation reference.
- Workflow guide and document templates.
- Troubleshooting guide.
- Test scenario reference with more than 20 scenarios.
- Migration checklist.
- Typed sync and async Python helper.
- Typer CLI.
- Pytest suite with more than 20 tests.
- Runnable examples.
- Python packaging files.

### Changed

- Expanded benchmarks for residential, office, retail, clinic, shell-to-finish, room, and trade-level estimates.
- Added VAT, compliance, quote review, and risk logic.
- Reworked voice to be neutral and imperative.

### Removed

- Promotional wording.
- Visual identity assets and image references.
- Named-credit metadata.

## [1.0.0] - 2025-01-01

### Added

- Initial estimator package.
