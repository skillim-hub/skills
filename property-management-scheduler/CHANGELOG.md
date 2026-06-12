# Changelog

All notable changes to this package are documented in this file.

## [2.2.0] - 2026-06-04

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, short snippets, status tags, and package actions.
- Added verified constants and `official_reference_values()` for VAT, Israel Invoices thresholds, and the Bank of Israel series API base.
- Added `reference-values` CLI command for printing validated operational reference values.
- Added tests for 2026 Israel Invoices thresholds and Bank of Israel host correction.

### Changed

- Corrected the Bank of Israel series API base to `edge.boi.gov.il` after the second-pass source contradicted an older indexed host.
- Updated Israel Invoices threshold wording to ₪10,000 before VAT from 01/01/2026 and ₪5,000 before VAT from 01/06/2026.
- Updated English and Hebrew guides with web-validated Israeli checkpoints.
- Expanded the API reference with Tax Authority API registration, Israel Invoices endpoint examples, privacy controls, arnona notes, and webhook applicability.
- Updated Hebrew QA terminology for מע"מ, מספר הקצאה, מס תשומות, שער יציג, מאגר הסדרות, ארנונה, and הנהלת חשבונות.

### Verified

- Standard VAT rate is 18% from 01/01/2025 and remains the current 2026 reference rate in the package.
- Israel Invoices allocation thresholds are ₪20,000 for 2025, ₪10,000 from 01/01/2026, and ₪5,000 from 01/06/2026.
- Israel Invoices threshold values are before VAT.
- Israel Tax Authority API access requires software-house and developer registration before developer-portal documentation.
- Israel Invoices allocation endpoint path uses `/shaam/production/Invoices/v2/Approval` for production examples.
- Data.gov.il uses a CKAN-style Action API, so the package keeps `/api/3/action/package_search` examples.
- Bank of Israel publishes representative exchange rates on foreign-currency business days.
- Bank of Israel series API base was corrected to the current `edge.boi.gov.il` host after second-pass validation.
- Residential rental income exemption ceiling for 2026 is ₪5,654 per month as an accountant-review reference.
- Residential rental income 10% route payment deadline is no later than 31/01 of the following year.
- Rental and Lending Law remains the official civil-law reference for landlord-tenant relationships.
- Maintenance triage must stay operational and must not automate legal advice, deadlines, or rent deductions.
- Protection of Privacy data-security obligations can apply to private-sector databases.
- Amendment 13 terminology is current by 2026 and requires production review for notice, registration, and security-level duties.
- Arnona is a local-authority property tax relevant to property records.
- Webhook event names are not official because the package is local-first and implements no external webhook provider.

The format follows Keep a Changelog, and this project follows semantic versioning.

## [2.1.0] - 2026-06-04

### Added

- Added deep neutrality audit report.
- Added Hebrew quality review log.
- Added installable `property_management_scheduler` package.
- Added Typer command-line entry point.
- Added script-level underscored client helper.

### Changed

- Moved the real client implementation into the importable package layout.
- Updated README installation steps to use `pip install -e .` and development requirements.
- Updated quick start to extract ids and reuse them in chained commands.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print readable Hebrew JSON.
- Expanded tests and retained async coverage.

### Removed

- Removed the hyphenated client script.
- Removed public Markdown emoji and visual asset patterns.

## [2.0.0] - 2026-06-04

### Added

- Added English and Hebrew guides.
- Added workflow, troubleshooting, test scenario, and migration references.
- Added Python client, command-line helper, examples, tests, package metadata, license, and development configuration.
