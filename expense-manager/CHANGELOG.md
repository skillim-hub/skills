# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and the project uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Web-validated `references/verification-log.md` with Pass 1 and Pass 2 source columns, official snippets, access date, and summary counts.
- Official Invoice Israel API endpoint reference for Approval, MultiApproval, invoice-information details, confirmation-number lookup, and decision-service caveats.
- 2026 validation notes for VAT, Osek Patur ceiling, Invoice Israel allocation thresholds, and uniform-file compatibility boundaries.
- Additional regression test confirming the 2026 VAT default is 18%.

### Changed

- Corrected gross-to-net VAT calculations from 17% to 18% for Israeli tax invoices dated from 01/01/2025 onward.
- Updated English and Hebrew examples from ₪117 gross equals ₪100 net and ₪17 VAT to ₪99.15 net and ₪17.85 VAT.
- Updated API/reference response examples for ₪234 gross to ₪198.31 net, ₪35.69 input VAT, and ₪23.79 mixed-use VAT recovery.
- Clarified that exported CSV/JSON packages are accountant-ready handoff files and not certified registered bookkeeping software or official uniform-structure files.
- Clarified domestic hospitality as a conservative review default rather than an absolute legal conclusion.
- Clarified mixed-use vehicle VAT as a configurable helper default rather than a universal rule.

### Verified

- Pass 1 confirmed official VAT history, Tax Authority interpretation, Invoice Israel allocation thresholds, Osek Patur 2026 ceiling, Tax Authority API registration, and uniform-file references.
- Pass 2 rechecked the same rows using separate Tax Authority service pages, execution instructions, topic pages, software-registration sources, and professional guidance.
- One official-document discrepancy remains for decision-service endpoint naming in secondary material; the package therefore documents the caveat and performs no live calls.

## [2.1.0] - 2026-06-01

### Added

- Neutrality and public-Markdown audit report.
- Hebrew QA log covering terminology, date localization, neutral imperative phrasing, and technical prose checks.
- Installable `expense_manager` package facade for direct imports without path manipulation.
- Record creation and id-based classification flow for chained CLI quick starts.
- Additional CLI and client tests for created-record workflows.

### Changed

- Moved the real client implementation from the hyphenated client filename into `scripts/expense_manager_client.py`.
- Updated README installation to use `pip install -e .` followed by development requirements.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Updated Hebrew examples to prefer `DD/MM/YYYY` and more natural Israeli professional terminology.
- Updated project packaging so `from expense_manager import ...` works after editable installation.

### Removed

- Hyphenated client implementation file.
- Cached pytest and Python bytecode artifacts from the distributable archive.

## [2.0.0] - 2026-06-01

### Added

- Comprehensive English operating guide with examples, decision trees, edge cases, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew operating guide with Israeli professional terminology, ₪ amounts, and `DD/MM/YYYY` examples.
- Regulation and API-style reference covering Israeli tax/VAT sources, local helper contracts, examples, and error tables.
- End-to-end workflow guide for Osek Patur, Osek Murshe, home office, vehicle, software, accountant import, and consumer tracking.
- Dedicated troubleshooting guide.
- Test-scenario catalog with 30 concrete scenarios.
- Migration checklist for replacing older spreadsheets and ad-hoc workflows.
- Typed Python client with synchronous and asynchronous classification helpers.
- Typer-based CLI.
- Pytest suite with more than 20 tests.
- Five runnable scenario examples.
- Project packaging files, development requirements, README, and MIT license.

### Changed

- Renamed skill slug to `expense-manager`.
- Expanded metadata tags and bumped version to `2.0.0`.
- Rebuilt exports around accountant-ready CSV, JSON summary, import mapping, and SHA-256 manifest.
- Replaced loose categorization guidance with deterministic helper functions and review flags.

### Removed

- Non-neutral presentation marks, distribution callouts, and creator metadata field.
