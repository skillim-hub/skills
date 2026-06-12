# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Two-pass web verification log covering VAT context, Arnona terminology, municipal collection responsibility, payment methods, installment variation, privacy, digital signatures, bookkeeping references, and API/webhook scope.
- Official-source correction notes for VAT and municipal profile URLs.
- Workflow, troubleshooting, and test-scenario coverage for VAT/accounting context.

### Changed

- Updated default Tel Aviv-Yafo, Jerusalem, and Haifa profile URLs to more specific official municipal service/payment pages.
- Reworded API examples as fictional adapter examples using `.invalid` hosts.
- Clarified that the package does not provide or assume a uniform national Arnona payment API or official webhook event vocabulary.
- Clarified in English and Hebrew guides that VAT must not be used to calculate Arnona payment amounts.

### Verified

- Pass 1 and Pass 2 both confirmed the current published VAT rate as 18% from 01/01/2025 for general accounting context.
- Pass 1 and Pass 2 both confirmed that Arnona is handled locally by municipalities/local authorities and that rates, identifiers, and payment channels vary.
- Pass 1 and Pass 2 did not confirm any uniform national Arnona payment API, endpoint paths, or official webhook event names; examples remain non-live adapter shapes.

## [2.1.0] - 2026-06-02

### Added

- Branding and attribution audit report.
- Hebrew quality-assurance log.
- Installable Python package with `from arnona_payment_reminder import ...` support.
- Console entry point through `arnona-payment-reminder`.
- Create-to-plan command flow that returns an id and reuses it in `plan-id`.

### Changed

- Replaced the hyphenated client filename with an underscored compatibility module and installable package implementation.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and indentation.
- Updated Hebrew user-facing dates to DD/MM/YYYY.
- Updated development installation instructions to use editable installation and the development requirements file.

### Removed

- Public Markdown emoji, visual presentation references.
- Importlib loading patterns from user-facing quick-start examples.

## [2.0.0] - 2026-06-02

### Added

- Payment-reminder-focused English guide.
- Hebrew guide with localized terminology, ₪ formatting, and DD/MM/YYYY user-facing dates.
- Regulatory and adapter reference for Arnona payment workflows.
- End-to-end workflow guide for households, small businesses, freelancers, landlords, overdue bills, standing orders, corrected vouchers, and accounting close.
- Troubleshooting guide.
- Test scenario catalog with more than 20 scenarios.
- Migration checklist from calculator and optimizer workflows.
- Typed sync and async Python client.
- Click-based CLI.
- Pytest suite with more than 20 tests.
- Five runnable example scripts.
- MIT license with a neutral rights holder.
- Development configuration through `pyproject.toml` and `requirements-dev.txt`.

### Changed

- Reframed the package from rate optimization to payment reminders and safe payment execution.
- Replaced creator and branding metadata with neutral metadata.
- Added receipt-first paid-status policy.
- Added overdue current-balance checks.
- Added standing-order duplicate-payment prevention.

### Removed

- Creator field from metadata.
- Non-neutral presentation assets and distribution callouts.
- Any workflow that treats calculated estimates as official payment amounts.

## [1.2.0] - Previous package

### Notes

- Earlier content focused on Arnona calculation, discounts, and appeals. Migration guidance appears in `references/migration-checklist.md`.
