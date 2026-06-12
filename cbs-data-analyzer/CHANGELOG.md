# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Web validation log under `references/verification-log.md` with two-pass source checks, snippets, URLs, access date, and status tags.
- Documented CBS `User-Agent` requirement and `download=false` usage in API guidance.
- Documented CBS Price Indices parameters `startPeriod`, `endPeriod`, `last`, and `coef`.
- Added sync and async client support for `start_period`, `end_period`, `last`, `coef`, and `download`.
- Added CLI options `--start-period`, `--end-period`, `--last`, and `--coef/--no-coef`.
- Added tests for documented optional price-index parameters.
- Added explicit web-verified VAT note for `18%` in 2026, with instruction to recheck before tax guidance.
- Added webhook non-applicability note.

### Changed

- Changed CPI code guidance from assumed default to catalog-verified use of documented example code `120010`.
- Updated default client `User-Agent` to `cbs-data-analyzer/2.2`.
- Updated README quick start to request the last six observations from the CBS API.
- Expanded API reference with current official source details from the two-pass validation.

### Not confirmed

- Did not add a current Invoice Israel threshold because the official 2026 threshold was not double-confirmed during the second pass.

## [2.1.0] - 2026-06-02

### Added

- Branding and identity audit report under `references/branding-audit.md`.
- Hebrew quality-assurance log under `references/hebrew-qa-log.md`.
- Editable-install configuration and console script entry point.

### Changed

- Moved the real Python implementation to underscore-named importable modules.
- Updated README installation to `pip install -e .` followed by `pip install -r requirements-dev.txt`.
- Updated quick-start commands to extract an index identifier from a JSON catalog response and reuse it in the next fetch command.
- Updated examples to accept `--env sandbox|production`, read environment variables, and emit JSON with `ensure_ascii=False` and `indent=2`.
- Refined Hebrew terminology, removed duplicated checklist text, and standardized Hebrew-facing dates as `DD/MM/YYYY`.

### Removed

- Hyphenated Python implementation files that could not be imported as normal modules.
- Runtime install artifacts and bytecode caches from the distributable package.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with decision tree, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew guide with Israeli professional terminology, `₪`, and `DD/MM/YYYY` localization.
- API and regulation reference covering CBS, data.gov.il, related official sources, request/response examples, and error handling.
- End-to-end workflow guide for rent indexation, small-business pricing, location screening, supplier clauses, housing trends, freelancer rates, consumer budgets, and construction escalation.
- Standalone troubleshooting guide.
- Test-scenarios reference with more than twenty validation cases.
- Migration checklist for spreadsheets and older scripts.
- Typed synchronous and asynchronous Python client.
- Typer CLI for catalog search, index fetching, indexation, market brief, and data.gov.il discovery.
- Offline pytest suite with more than twenty tests.
- Runnable examples for common scenarios.
- Project configuration, development requirements, README, and MIT license.

### Changed

- Replaced ad hoc helper behavior with reusable client methods.
- Replaced hard-coded economic snapshot guidance with live-fetch-first guidance and fixture-based tests.
- Expanded metadata tags and capabilities.

### Removed

- Creator metadata.
- Branding strings, visual assets, and distribution callouts.
- Hard-coded current economic claims that require live verification.
