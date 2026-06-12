# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog principles, and this package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Two-pass web verification log with source snippets, URLs, access dates, and  / → / final  status.
- Web-validated notes for the current Israeli VAT rate, open-banking consent terminology, supervised Israeli banks and acquirers, privacy/data-security references, and bookkeeping documentation.
- Explicit note that webhook event names are not implemented by this package.

### Changed

- Corrected API reference language: example API hosts and endpoint paths are illustrative and not official universal Israeli open-banking endpoints.
- Clarified that the package categorizes local CSV-style exports and does not claim bank endorsement, partnership, certified integration, uniform export format, or live account access.
- Updated English and Hebrew guides with the verified 18% VAT-rate note and a requirement to re-check tax rates before filing.
- Added `references/verification-log.md` to README file index.

### Verification findings

- Pass 1 and Pass 2 double-confirmed the 18% VAT rate from 01/01/2025 using Tax Authority pages.
- Pass 1 and Pass 2 double-confirmed Bank of Israel open-banking consent terminology.
- Pass 1 and Pass 2 double-confirmed supervised bank and acquirer names from Bank of Israel pages.
- Pass 1 found that API example hosts and paths were not official universal endpoints; Pass 2 confirmed the correction against Bank of Israel standards pages.
- Pass 1 found that the marketing phrase about automatic categorization was not an official bank or regulator claim; Pass 2 confirmed the correction to offline local categorization.

## [2.1.0] - 2026-06-02

### Added

- Branding and attribution audit report.
- Hebrew quality-assurance log.
- Installable `bank_transaction_categorizer` Python package.
- Registered input-id workflow for sample creation and follow-up categorization.
- Environment-aware examples that accept `--env sandbox|production`.
- `pytest-asyncio` development dependency.
- Syntax verification with `python -m compileall scripts/ -q`.

### Changed

- Moved the real client implementation from the hyphenated script filename into an importable package module.
- Updated README installation instructions to use `pip install -e .` and development requirements.
- Updated examples to read environment variables and emit JSON with `ensure_ascii=False` and `indent=2`.
- Updated Hebrew documentation to use neutral imperative wording and DD/MM/YYYY examples.

### Removed

- Hyphenated client implementation file from `scripts/`.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English and Hebrew guides.
- Israeli API/regulatory reference.
- Workflow, troubleshooting, test-scenario, and migration references.
- Typed sync/async client.
- Typer CLI with argparse fallback.
- Pytest suite with more than twenty tests.
- Five runnable examples.
- MIT license, project metadata, and development requirements.

### Changed

- Rebuilt as neutral offline-first package for Israeli transaction categorization.
- Expanded categories for taxes, wallets, bank fees, card settlements, and local merchants.
- Improved Hebrew CSV parsing and Israeli amount/date handling.

### Removed

- Branding, logos, badges, banners, organization callouts, and personal attribution metadata.
