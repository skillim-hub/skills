# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, and access date.
- Added 2026 web-validated planning assumptions to English and Hebrew guides.
- Added stale-rate troubleshooting and annual web-validation workflow guidance.

### Changed

- Bumped the package version to 2.2.0.
- Updated self-employed default planning rates to 7.70% and 18.00% for standard adult planning.
- Updated employer Form 102 resident-employee combined planning rates to 8.78% and 19.77%.
- Updated the no-income consumer default to ₪266 per month.
- Converted `scripts/bituach_leumi_payment_scheduler_client.py` to a compatibility wrapper around the installable package to prevent duplicate stale implementations.

### Fixed

- Corrected stale 2026 rate defaults found during Pass 1 and double-confirmed or corrected during Pass 2.
- Documented that VAT is verified as 18% in 2026 but remains outside scheduler calculations.
- Documented that no public scheduling API or webhook event names are used by this local helper.

## [2.1.0] - 2026-06-02

### Added

- Added a saved branding and authorship audit report.
- Added a Hebrew quality-assurance log covering localization, terminology, and date formatting.
- Added installable Python package layout with a console entry point.
- Added `create` and `show` CLI commands so a plan id from the create response can be reused in a later command.
- Added DD/MM/YYYY date parsing for Israeli-facing workflows.

### Changed

- Removed the hyphenated client module and moved imports to the installable package plus an underscored compatibility entry point.
- Updated README installation to use editable installation and development requirements.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and two-space indentation.
- Bumped metadata version and expanded operational tags.

### Fixed

- Confirmed no hosted visual asset references, public Markdown emoji, or non-neutral authorship fields remain.
- Confirmed Hebrew technical prose uses unpointed text and Israeli date/currency localization.

## [2.0.0] - 2026-06-02

### Added

- Added comprehensive English and Hebrew guides.
- Added API and regulation reference, workflow guide, troubleshooting guide, test scenarios, migration checklist, examples, CLI, client helper, tests, README, license, and project configuration.
