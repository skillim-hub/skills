# Changelog


## [1.3.0] - 2026-06-04

### Added
- Added web-validated `references/verification-log.md` with mandatory two-pass validation rows, snippets, access date, and summary counts.
- Added current Israeli VAT constant and Israel Invoice 2026 threshold helper methods to the Python client.
- Added regression tests for 2026 VAT rate, Israel Invoice thresholds, and ten-year residential lease coverage.

### Changed
- Updated VAT drafting language to use 18% as the verified current standard Israeli VAT rate as of 04/06/2026.
- Corrected residential apartment VAT guidance to reference the general exemption for residential rental up to 25 years, subject to statutory exceptions.
- Corrected covered residential lease screening from under ten years to not more than ten years.

### Verified
- Double-confirmed Israeli VAT rate, Fair Rent amendment topics, residential guarantee cap, ₪20,000 rent screen, arnona holder principle, business licensing dependency, and Israel Invoice 2026 thresholds.

All notable changes to this package are documented in this file. The format follows Keep a Changelog and the versioning style follows semantic versioning.

## [1.2.0] - 2026-06-04

### Added

- Added an installable `lease_agreement_drafter` Python package.
- Added `references/branding-audit.md` for neutral branding verification.
- Added `references/hebrew-qa-log.md` for Hebrew terminology and localization changes.
- Added import-safe script wrappers using underscored module names.
- Added environment-aware examples that accept `--env sandbox|production` and emit JSON with `ensure_ascii=False` and indentation.

### Changed

- Replaced hyphenated client script implementation with an importable module implementation.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to extract the draft id from the create response and use it in the audit step.
- Bumped package metadata version.
- Normalized Hebrew prose to professional Israeli terminology, neutral imperative voice, ₪ amounts, and DD/MM/YYYY dates.

### Removed

- Removed branding-sensitive names, visual links, header images, brand image references, and authorship fields.
- Removed public Markdown emoji.

## [1.1.0] - 2026-06-04

### Added

- Added bilingual operating guides, references, workflows, troubleshooting, tests, examples, README, license, and Python packaging files.

## [1.0.0] - 2026-06-04

### Added

- Initial lease agreement drafting package.
