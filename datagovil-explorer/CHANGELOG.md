# Changelog

All notable changes to this package are documented in this file. The format follows Keep a Changelog principles, and the package uses semantic versioning.

## [2.2.0] - 02/06/2026

### Added

- Added `references/verification-log.md` with two-pass web validation, official URLs, short snippets, access date, status tags, and summary counts.
- Added web-validation guidance to English and Hebrew skill files.
- Added package documentation for treating statutory rates, thresholds, quotas, and webhook claims as unconfirmed unless verified against an official source.

### Changed

- Bumped package metadata and installable project version to 2.2.0.
- Clarified that the `sandbox` environment selector is a user-provided test endpoint, not an official data.gov.il sandbox.
- Reworded rate-limit guidance so HTTP 429 handling is defensive and not presented as an official fixed quota.
- Updated Hebrew prose from forced terminology to natural professional phrasing.

### Verified

- Pass 1 confirmed data.gov.il portal purpose, CKAN API documentation, action paths, and VAT 18% from official or parliamentary sources.
- Pass 2 confirmed the same rows using different official or CKAN sources where possible.
- Corrected the sandbox wording after validation did not find an official sandbox host.
- Left fixed quotas and webhook event names as final unconfirmed rows in the verification log.

## [2.1.0] - 02/06/2026

### Added

- Added `references/branding-audit.md` with direct branding and provenance audit results.
- Added `references/hebrew-qa-log.md` with terminology and localization corrections.
- Added installable package module `datagovil_explorer` so `from datagovil_explorer import DatagovClient` works after `pip install -e .`.
- Added environment-aware CLI and examples with `--env sandbox|production`.
- Added helpers for extracting dataset and resource identifiers from chained responses.

### Changed

- Renamed Python files from hyphenated script names to importable underscore names.
- Updated installation instructions to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Israeli date formatting to DD/MM/YYYY.
- Updated CSV export default encoding to UTF-8 with signature for spreadsheet compatibility.

### Removed

- Removed generated pytest cache files from the bundle.
- Removed hyphenated client and test filenames.
- Removed public Markdown emoji and public visual references.

## [2.0.0] - 02/06/2026

### Added

- Added English and Hebrew skill guides.
- Added CKAN API reference, workflow guide, troubleshooting guide, test scenarios, and migration checklist.
- Added typed synchronous and asynchronous client.
- Added Click CLI, runnable examples, pytest suite, project metadata, license, and packaging files.
