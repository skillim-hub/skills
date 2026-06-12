# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [1.2.0] - 2026-06-04

### Added

- Added `references/verification-log.md` with two-pass web validation for Israeli VAT, open-data APIs, locality data, Companies Registrar data, privacy law, data-security regulations, Amendment 13, anti-spam consent, consumer-protection terminology, accessibility, telephone numbering, Meta Lead Ads webhooks, and WhatsApp Business categories.
- Added source-validated notes to `references/api-reference.md`, including official host and endpoint references for optional enrichment.

### Changed

- Bumped package metadata and Python package version to `1.2.0`.
- Clarified that the exact lead-routing behavior is package functionality verified by tests, not a public external standard.
- Updated Israeli date display guidance to `DD/MM/YYYY` in English and Hebrew documentation.
- Added a VAT guardrail: do not calculate VAT in the router; route billing matters to qualified finance staff and re-check official sources before invoice handling.
- Refined Hebrew wording for plural imperative voice, professional terminology, and agreement correctness.

### Verified

- Pass 1 confirmed the Israeli VAT rate, official open-data APIs, privacy, anti-spam, consumer, accessibility, telephone-numbering, Companies Registrar, Meta Lead Ads, and WhatsApp Business documentation.
- Pass 2 re-validated each confirmed row using a different official, authoritative, or independent source where available.
- Final unmatched item: no official public source exists for the exact package description sentence; documentation now labels it as package behavior rather than an external factual claim.

## [1.1.0] - 2026-06-04

### Changed

- Converted the client and CLI to an installable `lead_router` package.
- Replaced hyphenated script filenames with underscored compatibility wrappers.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Added a create-then-route quick start that extracts `lead_id` from the create response.
- Updated all runnable examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Expanded tests to cover stored lead creation and CLI route chaining.
- Added branding audit and Hebrew quality assurance logs.

### Fixed

- Removed importlib-based quick starts and script-path loading from public documentation.
- Confirmed public Markdown contains no emoji, badge URLs, logo references, or banner images.
- Refined Hebrew terminology, date formatting, and neutral imperative phrasing.

## [1.0.0] - 2026-06-04

### Added

- Comprehensive English skill guide with examples, decision tree, edge cases, anti-patterns, troubleshooting, and production checklist.
- Hebrew skill guide with Israeli professional terminology, ₪ examples, and DD/MM/YYYY date style.
- Integration and compliance reference with request/response examples and error tables.
- End-to-end workflow guide for web forms, WhatsApp, phone notes, CSV backfills, CRM handoff, escalation, and reporting.
- Dedicated troubleshooting guide.
- Test scenario reference with more than 20 concrete scenarios.
- Migration checklist for moving from manual assignment or spreadsheet workflows to deterministic routing.
- Typed sync and async Python client.
- Typer CLI for single-lead, JSON, batch CSV, explain, and config validation commands.
- Pytest suite with more than 20 tests.
- Runnable scenario scripts under `scripts/examples/`.
- MIT license using neutral copyright wording.
- Python project metadata and development requirements.

### Changed

- Replaced stub content with a production-oriented package.
- Bumped package metadata from `0.1.0` to `1.0.0`.
- Expanded tags and supported use cases.

### Removed

- Stub-only content.
- Non-neutral metadata.
- Non-neutral distribution callouts and visual promotional references.
