# Changelog

All notable changes to this skill package are documented in this file.

The format is based on Keep a Changelog. Versioning follows semantic versioning where practical.



## [2.1.0] - 2026-06-02

### Added

- Web-validated verification log with Pass 1 and Pass 2 sources for Israeli VAT, Israel Invoice, VAT-exempt threshold, cash-law, consumer cancellation, software registry, and terminology checks.
- Verified 2026 parameter tables in English, Hebrew, and API reference documents.
- Explicit note that no official webhook event names were confirmed for this non-integrating helper.

### Changed

- Set package version to 2.1.0.
- Updated Israel Invoice threshold guidance to the verified 2026 schedule: ₪10,000 before VAT from 01/01/2026 through 31/05/2026, and ₪5,000 before VAT from 01/06/2026.
- Added 2026 VAT-exempt dealer ceiling of ₪122,833.
- Added conditional consumer cancellation-fee language: 5% or ₪100, whichever is lower, when the statutory cancellation framework applies.
- Added cash-law review caution for business transactions above ₪6,000.

### Verification findings

- Pass 1 and Pass 2 double-confirmed the 18% VAT rate and 2026 Israel Invoice thresholds.
- Pass 1 and Pass 2 double-confirmed the 2026 VAT-exempt turnover ceiling.
- Pass 1 and Pass 2 double-confirmed the consumer cancellation-fee cap.
- Pass 1 and Pass 2 did not confirm any official webhook event names for this workflow.
- Deposit-specific blanket treatment for refundable security deposits could not be confirmed from official sources, so the package keeps conditional wording and professional-review warnings.

## [2.0.1] - 2026-06-02

### Added

- Neutrality and visual-reference audit report.
- Hebrew QA log with terminology and localization changes.
- Editable-install workflow and console-script entry point.
- Example scripts that read environment variables and accept `--env sandbox|production`.
- Settlement deposit-reference field for chaining create-record output into final settlement.

### Changed

- Deleted the hyphenated client script and kept the implementation in the underscored client module.
- Updated README installation to `pip install -e .` followed by development requirements.
- Updated Hebrew date examples to DD/MM/YYYY.
- Updated project metadata for installable module imports.

### Fixed

- Added DD/MM/YYYY parsing support.
- Removed path-hack imports from examples.
- Added compile-time validation to the release process.


## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with decision trees, examples, edge cases, anti-patterns, troubleshooting table, and production checklist.
- Full Hebrew guide with Israeli professional terminology, ₪ formatting, and DD/MM/YYYY examples.
- Regulatory and local helper API reference.
- End-to-end workflow guide.
- Dedicated troubleshooting reference.
- Test scenarios reference with 30 concrete scenarios.
- Migration checklist for moving from legacy spreadsheets or manual workflows.
- Typed Python client with sync and async facades.
- Typer CLI and argparse helper.
- Runnable example scripts.
- Pytest suite with 20+ tests.
- Python project metadata and development requirements.
- MIT license with neutral copyright holder.

### Changed

- Removed branding, visual marks, person/entity attribution metadata, and distribution callouts.
- Reworked tone to neutral imperative guidance.
- Expanded metadata tags and bumped package version.

### Fixed

- Added controls to prevent double VAT, duplicate deposit application, and incorrect treatment of refundable deposits.
