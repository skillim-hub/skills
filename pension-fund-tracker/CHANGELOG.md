# Changelog

All notable changes to this package are documented in this file.

The format is based on Keep a Changelog, and this package follows semantic versioning.

## [1.2.0] - 2026-06-02

### Added
- Added `references/verification-log.md` with two-pass web validation, source snippets, access dates, and status tags.
- Added a verified source baseline to `references/api-reference.md`.

### Changed
- Clarified that the authoritative pension public-data publisher is the Capital Market, Insurance and Savings Authority, with legacy Ministry of Finance references treated as government provenance.
- Clarified that Israeli VAT was verified at 18% for 2026 but is not used in pension-return or management-fee calculations.
- Replaced placeholder `RESOURCE_ID` examples with `DISCOVERED_RESOURCE_ID` where the value must be discovered from Data.gov.il.

### Verified
- Pass 1 confirmed Pensia Net purpose, source assumptions, returns, fees, Data.gov.il dataset, CKAN endpoint paths, VAT, and licensed-advice boundaries.
- Pass 2 double-confirmed each row using different official or independent sources where possible.
- Corrected the API reference so example resource IDs cannot be mistaken for Pensia Net resource IDs.

## [1.1.0] - 2026-06-02

### Added
- Added installable `src/pension_fund_tracker` package.
- Added branding audit and Hebrew QA log references.
- Added examples with environment variables, `--env sandbox|production`, and JSON output using `ensure_ascii=False` with indentation.
- Added `pytest-asyncio` to development requirements.

### Changed
- Deleted the hyphenated client implementation and moved supported client code to underscored/package modules.
- Updated installation instructions to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick-start flow to extract a fund id from normalized output and reuse it in the compare step.
- Localized Hebrew-facing dates to DD/MM/YYYY.

### Fixed
- Removed file-based import hacks from tests and examples.
- Confirmed public Markdown contains no emoji or visual-asset references.

## [1.0.0] - 2026-06-02

### Added

- Comprehensive English and Hebrew skill guides.
- API and regulatory reference for official Israeli public-data workflows.
- End-to-end workflow guide.
- Troubleshooting guide.
- Test-scenarios reference with 30 concrete scenarios.
- Migration checklist.
- Typed synchronous and asynchronous Python client.
- Typer CLI for normalization, validation, ranking, comparison, CKAN fetch, scoring, and fee-impact estimation.
- Pytest suite with more than 20 tests.
- Runnable examples.
- README, MIT license, project metadata, and development requirements.

### Changed

- Bumped version from `0.1.0` to `1.0.0`.
- Replaced stub content with production-ready guidance.
- Expanded metadata tags.

### Removed

- Removed non-neutral metadata.
- Removed non-neutral presentation and distribution phrasing.
