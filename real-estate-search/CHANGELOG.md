# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [1.3.0] - 04/06/2026

### Added
- Added `references/verification-log.md` with two-pass web validation, short source snippets, access date, and summary counts.
- Added tests for verified Komo city paths, Komo room parameters, Yad2 commercial routing, and Madlan commercial routing.

### Changed
- Corrected Komo source generation from an unverified generic `/search` path to verified `/code/nadlan/apartments-for-rent.asp` and `/code/nadlan/apartments-for-sale.asp` city-page patterns.
- Corrected Yad2 commercial searches to use `/realestate/commercial`.
- Corrected Madlan commercial searches to use `/commercial/for-rent` and `/commercial/for-sale`.
- Clarified that Komo neighborhood filtering must be applied manually unless a verified neighborhood id is available.
- Bumped package and metadata version to `1.3.0`.

### Verified
- Pass 1 and Pass 2 confirmed the standard Israeli VAT assumption of 18% from 01/01/2025 using official sources.
- Pass 1 and Pass 2 confirmed official terminology for land registry, purchase tax simulator, planning information, arnona, business licensing, accessibility, consumer protection, privacy, broker registry, residential lease law, and data.gov.il CKAN documentation.

### Fixed
- Fixed Hebrew wording in the decision tree from an incorrect phrase to `מע״מ`.

## [1.2.0] - 04/06/2026

### Added

- Added an installable `src/real_estate_search` Python package.
- Added a Typer CLI entry point named `real-estate-search`.
- Added `references/branding-audit.md` with package-wide audit results.
- Added `references/hebrew-qa-log.md` with Hebrew quality review notes.
- Added `scripts/real_estate_search_client.py` as the underscored script import entry.
- Added a sixth runnable example for rental cash estimation.
- Added async link-check placeholder support with no network call by default.
- Added CLI `show` command that validates a `plan_id` extracted from `create` output.

### Changed

- Removed the hyphenated Python client module.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to save a create response, extract `plan_id`, and use it in the next step.
- Updated all examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Expanded Hebrew guidance with Israeli terminology for rentals, purchases, commercial use, taxation, municipal classification, and licensing.
- Bumped metadata version to `1.2.0`.

### Fixed

- Removed public Markdown emoji.
- Removed visual-mark and image references.
- Removed creator and byline metadata.
- Preserved the required MIT license holder line.
- Added `pytest-asyncio` to development requirements.

## [1.1.0] - 03/06/2026

### Added

- Added bilingual English and Hebrew skill guides.
- Added source reference, workflow guide, troubleshooting guide, test scenarios, migration checklist, README, changelog, license, packaging metadata, CLI helper, and pytest suite.

## [1.0.0] - 03/06/2026

### Added

- Initial real-estate search helper content.
