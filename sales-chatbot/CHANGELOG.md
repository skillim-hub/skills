# Changelog

All notable changes to this skill are documented in this file.

The format follows Keep a Changelog, and versioning follows Semantic Versioning.

## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, and summary counts.
- Added verified Tax Authority invoice-allocation endpoint examples for `Invoices/v2/Approval` and `general-information/v2/MinimumAmount`.
- Added verified Bank of Israel SDMX exchange-rate API examples and date-filter guidance.
- Added verified WhatsApp Cloud API endpoint, opt-in, service-window, webhook field, status payload, and error-location notes.
- Added package tests for the web-validated VAT default and importable package exports.

### Changed

- Bumped the package to `2.2.0` after the web-validated final pass.
- Confirmed the Israeli VAT default remains `18%` from `01/01/2025`, with the code value kept configurable.
- Corrected the current invoice-allocation threshold guidance to above `₪5,000` before VAT as of `01/06/2026`, and directed implementations to fetch `MinimumAmount` before issuing invoices.
- Corrected currency-rate examples from a placeholder endpoint to the Bank of Israel SDMX endpoint on `edge.boi.gov.il`.
- Removed example `sys.path` fallback logic so examples rely on the installable package installed with `pip install -e .`.

### Validation findings

- Pass 1 and Pass 2 double-confirmed VAT, total-price display, anti-spam consent, privacy, accessibility, Tax Authority endpoints, Bank of Israel representative-rate API patterns, and WhatsApp Cloud API endpoint/webhook terminology.
- Pass 2 corrected invoice-allocation threshold wording from the staged `₪10,000` 2026 threshold to the current `₪5,000` threshold effective `01/06/2026`.
- Exact search for the generated capability sentence did not produce one official source; constituent claims are validated separately in the verification log.

## [2.1.0] - 2026-06-03

### Changed

- Moved the real client implementation to `scripts/sales_chatbot_client.py` and removed the non-importable hyphenated client module.
- Added importable package exports and console script configuration.
- Updated README installation and quick-start flow to use `pip install -e .`, development requirements, create-response ID extraction, and quote-status reuse.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with Hebrew preserved.
- Localized Hebrew dates to DD/MM/YYYY.

### Added

- Added branding audit and Hebrew QA log references.
- Added pytest-asyncio coverage and compile-time verification.

## [2.0.0] - 2026-06-03

### Added

- Comprehensive English guide with decision trees, edge cases, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew guide with Israeli sales terminology, ₪ pricing, DD/MM/YYYY dates, and tashlumim wording.
- Israeli API and regulatory reference covering messaging, payment, accounting, tax allocation, currency rates, shipping, consent, privacy, and common error tables.
- End-to-end workflow guide for WhatsApp, website chat, freelancers, retail, complaint handoff, opt-out, catalog release, B2B invoice requests, delivery exceptions, and subscriptions.
- Troubleshooting reference.
- Test scenario reference with 30 concrete scenarios.
- Migration checklist.
- Typed Python client with synchronous and asynchronous recommendation methods.
- Typer CLI with fallback mode.
- pytest suite with 20+ tests.
- Runnable example scripts.
- Project metadata, README, MIT license, pyproject, and development requirements.

### Changed

- Rebuilt the skill under the `sales-chatbot` slug.
- Replaced generic chatbot material with Israeli sales and service workflows.
- Made consent, handoff, and payment safety first-class behaviors.
- Bumped metadata version to 2.0.0.

### Removed

- Branding references.
- Decorative visual references.
- Individual attribution field in metadata.
