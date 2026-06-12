# Changelog

All notable changes to this package are documented in this file. The format follows Keep a Changelog, and versioning uses semantic versioning.

## [2.2.0] - 2026-06-01

### Added

- Added `references/verification-log.md` with a two-pass web validation table, source URLs, short source snippets, access date, status tags, and summary counts.
- Added official SHAAM host and endpoint constants for sandbox, production, single allocation approval, batch approval, and held-invoice decisions.
- Added tests for January 2026 threshold, June 2026 threshold, exact-threshold behavior, current 2026 VAT, and zero-rate allocation exclusion.

### Changed

- Corrected the allocation threshold schedule after web validation: 2025 remains ₪20,000.00, 01/01/2026 becomes ₪10,000.00, and 01/06/2026 becomes ₪5,000.00.
- Changed allocation logic from greater-than-or-equal to greater-than to match the official Hebrew wording `עולה על`.
- Changed allocation logic to require a non-zero VAT component.
- Changed the default client endpoint from `/allocations` to `/Invoices/v2/Approval` while documenting that production adapters must map the semantic payload to the official schema.
- Updated English and Hebrew public guides, API reference, workflow guide, troubleshooting guide, migration checklist, and test scenarios with the web-validated 2026 rules.

### Fixed

- Removed stale future annual threshold assumptions from documentation and tests.
- Clarified that `customer_type: business` represents an Israeli VAT-registered business customer for allocation checks.
- Clarified that no official invoice-allocation webhook event names are modeled.

## [2.1.0] - 2026-06-01

### Added

- Added branding and neutrality audit report.
- Added Hebrew QA log.
- Added installable `src/invoice_generator` package.
- Added console entry point `invoice-generator`.
- Added local document store so CLI quick-start flows can create a document, extract an id, and reuse that id in later commands.
- Added pytest-asyncio to development requirements.
- Added async client test coverage and CLI create-chain test coverage.

### Changed

- Replaced hyphenated Python implementation filenames with import-safe underscore wrappers.
- Moved real client and CLI implementation into the package module.
- Updated README installation instructions to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and indentation.
- Standardized Hebrew public documentation on ₪ amounts and `DD/MM/YYYY` dates.

### Fixed

- Fixed duplicated table cell rendering in Hebrew markdown output.
- Removed public Markdown emoji.
- Removed remaining visual promotional asset and ownership metadata risks.

## [2.0.0] - 2026-06-01

### Added

- Added English and Hebrew skill guides.
- Added allocation-number readiness checks.
- Added typed client, CLI, references, examples, and tests.
- Added MIT license with neutral placeholder.
