# Changelog

All notable changes to this package are documented in this file.

The format is based on Keep a Changelog, and this package follows semantic versioning.



## [2.2.0] - 2026-06-02

### Added

- Two-pass web validation log for official Israeli sources.
- Current verified baseline section for Bank of Israel rate, implied prime rate, VAT, CPI publication timing, and CBS CPI API endpoints.
- Optional CBS CPI API endpoint reference for external data-ingestion workflows.
- Troubleshooting note for stale prime-rate assumptions.
- Workflow for refreshing live public assumptions before a new decision.

### Changed

- Updated prime-linked examples from a stale 6.00% base assumption to the verified 5.25% implied prime base as of 2026-06-02.
- Clarified that VAT is not calculated by the planner and belongs in surrounding cash-flow workpapers.
- Clarified that `effective_cash_cost` is a planning metric and not an official lender IRR disclosure.
- Bumped package and metadata version to 2.2.0.

### Verified

- Pass 1 confirmed the VAT increase, Bank of Israel current rate, prime formula, CPI publication timing, CBS API endpoint family, and loan-fee terminology.
- Pass 2 rechecked the same rows using different official or corroborating sources where possible.
- No final unconfirmed regulatory/API rows remain.

## [2.1.0] - 2026-06-02

### Added

- Branding and packaging neutrality audit report.
- Hebrew quality-assurance log.
- Installable `loan_amortization_planner` package exports.
- Local scenario registry with create-and-schedule quick-start flow.
- Underscored script entry points.
- Environment-aware runnable examples with `--env sandbox|production`.
- `pytest-asyncio` development dependency.

### Changed

- Updated README installation flow to use editable installation.
- Updated quick start to extract a scenario id from a create response and reuse it in the next command.
- Localized Hebrew dates to `DD/MM/YYYY` and emphasized ₪ formatting.
- Replaced dynamic path imports with package imports.

### Removed

- Hyphenated Python script entry points.
- Public Markdown emoji, image references, and promotional packaging language.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with decision trees, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- Full Hebrew guide using Israeli business, accounting, and credit terminology.
- Offline API and regulatory reference for Israeli loan-planning assumptions.
- End-to-end workflow guide for offer comparison, freelancer cash flow, CPI stress tests, balloon loans, grace periods, approval packs, and reconciliation.
- Dedicated troubleshooting reference.
- Dedicated test-scenarios reference with 30 concrete scenarios.
- Migration checklist for replacing spreadsheets or prior versions.
- Typed Python helper with synchronous and asynchronous schedule and comparison functions.
- Typer CLI for schedule generation, scenario comparison, and validation.
- Runnable example scripts for fixed, prime, CPI, comparison, early repayment, and balloon scenarios.
- pytest suite with more than 20 tests.
- README, MIT license, pyproject, and development requirements.

### Changed

- Rebuilt the package with neutral language and no branding.
- Expanded metadata tags and bumped version.
- Standardized date support for `DD-MM-YYYY` and `YYYY-MM-DD`.
- Standardized money output to two decimal places.

### Removed

- Author metadata.
- Non-neutral packaging references.
- Image references.
- Promotional distribution language.
