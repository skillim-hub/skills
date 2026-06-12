# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [3.0.0] - 2026-06-05

### Added

- Added web-validated Israeli VAT, exempt-dealer, and allocation-number guardrails.
- Added English and Hebrew guides with decision trees, examples, troubleshooting, and anti-patterns.
- Added API and regulation reference with source URLs, access dates, and error tables.
- Added typed synchronous and asynchronous HTTP clients.
- Added CLI commands for VAT checks, encoding conversion, CSV/JSON conversion, invoice validation, sample config, and BTKN generation.
- Added BTKN staging-file generation with Windows-1255 output support.
- Added OPENFORMAT/BKMV dry-run skeleton helper for staging validation.
- Added multi-company configuration guidance.
- Added pytest coverage for calculations, validation, file handling, and sync/async transport behavior.

### Changed

- Renamed the package focus from generic data tools to integration workflows.
- Replaced legacy fixed-width assumptions with official-export-first guidance.
- Updated metadata to version `3.0.0` and expanded tags.

### Removed

- Removed author fields.
- Removed organization and distribution callouts.
- Removed decorative branding, badges, banners, and logos.
