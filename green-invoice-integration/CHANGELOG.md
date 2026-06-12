# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [3.0.0] - 2026-06-05

### Added

- Added web-validated API and regulation reference with current VAT and Israel Invoices thresholds.
- Added English and Hebrew operating guides with decision trees, examples, troubleshooting, and anti-patterns.
- Added typed synchronous and asynchronous Python client based on `httpx`.
- Added Typer CLI for authentication, customers, documents, payment-link request preparation, and webhook verification.
- Added pytest coverage for authentication, endpoints, validation, async calls, webhook signatures, and payload construction.
- Added troubleshooting and test-scenario references for sandbox and production cutover.

### Changed

- Updated token request payload to include `grant_type: client_credentials`.
- Updated base URL guidance to the current `api.greeninvoice.co.il/api/v1` path.
- Updated VAT examples to `18%` and allocation-number threshold handling to `₪5,000` from `01-06-2026`.
- Reworked language into neutral imperative voice.

### Removed

- Removed author metadata.
- Removed distribution branding and marketplace callouts.
- Removed legacy script naming.
