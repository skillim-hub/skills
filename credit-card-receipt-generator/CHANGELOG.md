# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project adheres to Semantic Versioning.

## [3.0.0] - 2026-06-04

### Added

- Added Israeli multi-gateway receipt workflow for Cardcom, Tranzila, Grow/Meshulam, and Pelecard.
- Added English and Hebrew skill guides with decision trees, examples, troubleshooting, and anti-patterns.
- Added web-validated API and regulation reference covering VAT, Osek Patur, Israel Invoices thresholds, official forms, and endpoint paths.
- Added typed sync and async Python client for normalization, validation, VAT splitting, and receipt rendering.
- Added Click CLI for JSON input, validation, sample generation, and endpoint lookup.
- Added pytest suite with gateway normalization, VAT, privacy, CLI, and async tests.

### Changed

- Renamed and refocused the package from a single-gateway payment guide to a neutral credit-card receipt generator.
- Updated Israeli VAT default to 18% and 2026 thresholds.
- Removed non-neutral package attribution and promotional presentation elements.

### Security

- Added detection for raw card numbers that pass Luhn validation.
- Added explicit anti-fabrication and no-CVV handling guidance.
