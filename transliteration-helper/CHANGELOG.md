# Changelog

All notable changes to this skill are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.


## [1.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation of official-source claims, VAT context, passport spelling bases, terminology, fees, forms, API scope, and webhook scope.

### Changed

- Corrected wording that could imply a single Ministry of Interior transliteration table produces one mandatory Latin spelling. Documentation now states that Israeli travel-document spelling may follow several permitted bases and that an existing official spelling must be preserved.
- Clarified that Academy simple transliteration is an official reference point for Hebrew-to-Latin transliteration, not a substitute for a passport, registry correction, or user-confirmed legal spelling.
- Clarified that VAT is outside the transliteration engine and should not be calculated inside transliteration examples without a separate tax workflow.
- Bumped metadata and package version to `1.2.0`.

### Verified

- Pass 1 confirmed official terminology for `תעתיק מעברית לאותיות לטיניות`, population-registry correction wording, and the 18% Israeli VAT context from official or recognized sources.
- Pass 2 confirmed the same claims through different queries and sources where available, including passport-regulation text and 2026 tax-summary sources.

## [1.1.0] - 2026-06-03

### Added

- Added a neutrality audit report under `references/branding-audit.md`.
- Added a Hebrew quality-assurance log under `references/hebrew-qa-log.md`.
- Added local record creation and lookup helpers for review workflows.
- Added CLI `create` and `show` commands for JSON Lines review records.
- Added installable console entry point through `pyproject.toml`.
- Added example scripts that read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and indentation.

### Changed

- Moved the real client implementation into `scripts/transliteration_helper_client.py`.
- Removed the hyphenated client module and updated imports, tests, examples, and documentation.
- Updated local development installation to `pip install -e .` followed by `pip install -r requirements-dev.txt`.
- Added `pytest-asyncio` to development requirements.
- Updated Israeli-facing date examples to `DD/MM/YYYY`.
- Revised Hebrew prose for neutral imperative phrasing and professional Israeli terminology.
- Bumped metadata version to `1.1.0`.

### Removed

- Removed shim-based client loading.
- Removed public Markdown emoji and remaining non-neutral image/distribution wording.

## [1.0.0] - 2026-06-03

### Added

- Comprehensive English guide with decision trees, edge cases, anti-patterns, troubleshooting summary, and production checklist.
- Comprehensive Hebrew guide with natural Israeli business terminology, ₪ examples, and `DD/MM/YYYY` date conventions.
- Local reference guide covering Python, async usage, CLI, schemas, warnings, errors, and standards context.
- End-to-end workflow guide for customer records, invoices, CRM cleanup, shipping exports, regulated forms, duplicate handling, overrides, and review queues.
- Dedicated troubleshooting guide.
- Test scenario guide with 30 concrete scenarios.
- Migration checklist for existing customer and supplier datasets.
- Typed Python client with synchronous, asynchronous, batch, file, JSON, CSV, and text output support.
- Click-based CLI with single-name, batch, and validation commands.
- Runnable examples for consumer, freelancer, CSV, review, and async workflows.
- pytest suite with more than 20 tests.
- README, MIT license, pyproject configuration, and development requirements.

### Changed

- Replaced stub content with a production-ready local transliteration package.
- Bumped metadata version from `0.1.0` to `1.0.0`.
- Expanded metadata tags for localization, Israeli workflows, customer data, CLI, validation, and batch processing.

### Removed

- Personal attribution metadata.
- Non-neutral distribution references.
- Public image references.
