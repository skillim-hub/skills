# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [3.0.0] - 2026-06-04

### Added

- Added web-validated API reference with current sandbox and production endpoint paths.
- Added 2026 allocation threshold handling, including the 01-06-2026 ₪5,000 threshold.
- Added typed sync and async Python client with validation helpers.
- Added Typer CLI for validation, threshold decisions, approval requests, batch requests, lookups, and held-invoice decisions.
- Added pytest suite with mocked HTTP transport.
- Added Hebrew guide with Israeli professional terminology and local formatting.
- Added troubleshooting playbook and acceptance scenarios.

### Changed

- Rebuilt documentation in neutral imperative voice.
- Replaced stale endpoint placeholders with documented Tax Authority paths.
- Updated VAT rate handling to 18% from 01-01-2025 onward.
- Bumped metadata version to 3.0.0 and expanded tags.

### Removed

- Removed author metadata.
- Removed branding, badges, logos, banners, and distribution callouts.
- Removed stale compatibility claims and unofficial endpoint assumptions.
