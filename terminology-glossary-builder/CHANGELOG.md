# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [1.2.0] - 03/06/2026

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, short snippets, access date, and summary counts.
- Added web-validated 2026 reference values for VAT, exempt dealer ceiling, invoice allocation thresholds, National Insurance rates, pension contribution tiers, consumer cancellation fees, and privacy database duties.
- Added an explicit webhook-events note stating that webhook event names are not applicable to this offline-first package.

### Changed

- Bumped package and metadata versions to `1.2.0`.
- Updated privacy terminology from `Database registration` to `Database registration or notice` where Amendment 13 requires more precise wording.
- Updated Hebrew terminology to `רישום או הודעה על מאגר מידע` and added an applicability warning.
- Added dated usage notes for 18% VAT, 122,833 ₪ exempt-dealer ceiling, 10,000 ₪ and 5,000 ₪ invoice allocation thresholds, National Insurance 2026 rates, and pension contribution tiers.

### Fixed

- Corrected stale privacy wording that implied database registration applies broadly after Amendment 13.
- Clarified that numeric rates, thresholds, and fees must be shown with DD/MM/YYYY validity or access dates.

## [1.1.0] - 03/06/2026

### Added

- Added `terminology_glossary_builder` as an installable Python package.
- Added Typer console entry points for `tgb` and `terminology-glossary-builder`.
- Added local create-export workflow with saved glossary ids.
- Added branding audit report.
- Added Hebrew QA log.
- Added compile-safe underscored script entry points.

### Changed

- Replaced hyphenated Python implementation filenames with importable package modules.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Expanded Hebrew localization requirements and professional terminology checks.

### Fixed

- Fixed import behavior so `from terminology_glossary_builder import GlossaryBuilder` works without path modification.
- Fixed quick-start instructions so the id from `create` is used in `export`.
- Removed public Markdown emoji, decorative visual brand assets, individual credits, and non-neutral distribution wording.

## [1.0.0] - 03/06/2026

### Added

- Added initial bilingual glossary builder guide.
- Added source registry for Israeli authorities.
- Added typed helper, CLI, examples, and pytest coverage.
