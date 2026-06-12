# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added two-pass web verification log at `references/verification-log.md`.
- Added verified 2026 source URLs for VAT, unemployment, disability, child allowance, income support, and privacy references.
- Added 2026 constants for unemployment daily ceilings, child allowance, general disability, income support caps, and vehicle screening limits.

### Changed

- Bumped package version from 2.1.0 to 2.2.0.
- Updated child allowance rates from 2025 values to 2026 values: ₪173 and ₪219 by birth order.
- Updated full general disability monthly amount from ₪4,290-era planning value to ₪4,711 for 2026.
- Replaced rough income-support threshold formula with a 2026 work-income cap table by age and household type.
- Changed income-support result amounts to `null` so the helper does not imply an official payment calculation.
- Tightened general disability medical-threshold logic to require 60%, or 40% with a 25% single impairment.
- Tightened general disability incapacity screening to recognized 60% and higher preliminary degrees.
- Updated English and Hebrew documentation with 2026 verified constants and official-source workflow.

### Fixed

- Fixed stale child allowance test expectation.
- Fixed disability screening false positive for 40% to 59% medical disability without a qualifying single impairment.
- Fixed stale income-support examples that used an unverified unverified preliminary cap.

## [2.1.0] - 2026-06-02

### Added

- Added neutrality audit report at `references/branding-audit.md`.
- Added Hebrew quality review log at `references/hebrew-qa-log.md`.
- Added installable Python package under `social_security_benefit_checker/`.
- Added import-safe client module at `scripts/social_security_benefit_checker_client.py`.
- Added package console command `social-security-benefit-checker`.
- Added chained create-and-check quick-start flow using `profile_id`.
- Added example script support for `--env sandbox|production`.
- Added expanded pytest coverage for profile validation, benefit checks, async methods, local storage, and direct script import.
- Added syntax compilation checks for scripts and package modules.

### Changed

- Bumped package version from 2.0.0 to 2.1.0.
- Replaced hyphenated client module path with an underscored client module path.
- Updated README installation instructions to use editable installation and development requirements.
- Updated examples to read environment variables and print JSON with `ensure_ascii=False` and indentation.
- Updated Hebrew documentation for neutral imperative phrasing, Israeli professional terminology, ₪ amounts, and DD/MM/YYYY dates.
- Updated packaging metadata to support ordinary imports without path manipulation.

### Removed

- Removed hyphenated client implementation file.
- Removed residual visual asset references and promotional wording.
- Removed public Markdown emoji characters.

## [2.0.0] - 2026-06-02

### Added

- Added bilingual English and Hebrew operating guides.
- Added references for local interfaces, workflows, troubleshooting, tests, and migration.
- Added typed sync and async helper.
- Added Typer-based CLI.
- Added runnable example scripts.
- Added pytest suite.
- Added MIT license.
- Added project metadata and development requirements.

### Changed

- Expanded scope from a narrow unemployment flow to unemployment, general disability, child allowance, and income supplement.

## [1.0.0] - 2026-06-02

### Added

- Initial local skill package structure.
