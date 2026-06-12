# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 04-06-2026

### Added

- Web-validated verification log with two-pass source checks.
- Summary counts for double-confirmed, corrected, and unconfirmed rows.
- Explicit validation notes for VAT, Tabu extract contents, digital extract status, payment wording, caveat terminology, mortgage terminology, Tabu-Net notifications, land-law references, privacy references, and electronic-signature references.

### Changed

- Clarified that `/tabu/parcel`, `/tabu/address`, and `/tabu/extract-orders` are internal adapter examples, not verified official public endpoint paths.
- Clarified that no official public Tabu JSON API host or webhook event names were confirmed in the two-pass validation.
- Kept land-registry fees configurable because current prices are published through official payment pages and can change.
- Kept VAT information in the verification log only because the package does not perform VAT calculation.

### Web validation findings

- Pass 1 confirmed the Tabu extract scope on gov.il Hebrew and English service pages.
- Pass 2 confirmed the Tabu extract scope against alternate gov.il and ministry pages.
- Pass 1 confirmed the VAT 18% rate from the Israel Tax Authority history page.
- Pass 2 confirmed the VAT effective date through the Knesset approval notice and Tax Authority terminology pages.
- Pass 1 found no specific official public Tabu JSON API endpoint in targeted public catalog checks.
- Pass 2 repeated endpoint and webhook checks and corrected package wording to adapter-only terminology.
- Final validation result: 20 checks, 17 double-confirmed, 3 corrected in pass 2, 0 final unconfirmed.

## [2.1.0] - 04-06-2026

### Added

- Installable `land_registry_tabu` package under `src/`.
- Console entry point: `land-registry-tabu`.
- Extract-order workflow with `create-order` and `order-status` commands.
- Local order fixture for order/status chaining examples.
- Environment-aware examples with `--env sandbox|production`.
- Branding and public-asset audit report.
- Hebrew quality review log.
- Public-method count verification.

### Changed

- Replaced hyphenated client script with underscored compatibility script.
- Updated examples to use package imports instead of path-based loading.
- Updated README install flow to use `pip install -e .`.
- Updated Hebrew-facing date style to `DD/MM/YYYY`.
- Updated tests for installable import and order workflow.
- Bumped version to 2.1.0.

### Fixed

- Removed previous changelog terms that matched the public-asset audit patterns.
- Added `pytest-asyncio` to development requirements.
- Ensured Markdown files contain no emoji.
- Ensured Hebrew technical prose contains no niqqud.

## [2.0.0] - 04-06-2026

### Added

- Comprehensive English guide with examples, edge cases, Mermaid decision trees, troubleshooting, anti-patterns, and a production checklist.
- Full Hebrew guide with Israeli terminology, local currency notation, and local date formatting.
- API and regulation reference covering Israeli land registry workflows, configurable endpoints, request/response examples, and error tables.
- End-to-end workflow guide for purchase, lease, collateral, business storefront, and consumer due-diligence scenarios.
- Dedicated troubleshooting reference.
- Dedicated test-scenarios reference with more than 20 concrete scenarios.
- Migration checklist for replacing manual spreadsheet and email workflows.
- Typed synchronous and asynchronous Python client.
- Click-based CLI with parcel, address, validation, normalization, and template commands.
- Pytest suite with more than 20 tests.
- Runnable examples and local fixture payloads.
- README, MIT license, pyproject, and development requirements.

### Changed

- Rebuilt package structure for neutral operational use.
- Removed non-neutral metadata and public image references.
- Expanded metadata tags and bumped version.

### Fixed

- Added consistent validation for parcel identifiers, Israeli IDs, share formats, dates, and warning extraction.
