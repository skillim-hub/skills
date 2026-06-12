# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog principles, and this package uses semantic versioning.

## [1.4.0] - 2026-06-03

### Added
- Added `references/verification-log.md` with two-pass web validation for Israeli regulatory and official-source claims.
- Added package constants for the current Israeli VAT rate and effective date.
- Added explicit non-API and non-webhook scope documentation for the local planner.

### Changed
- Corrected broad advertising-authority wording to a regulator-by-context model: Consumer Protection and Fair Trade Authority, Privacy Protection Authority, Ministry of Health, accessibility authority, and sector regulators.
- Updated launch checklist guidance to use 18% VAT from 01/01/2025 unless lawful exemption, zero-rate, or sector-specific treatment applies.
- Clarified Russian as a practical targeting and service-language option rather than an official-language claim.

### Verified
- Pass 1 and Pass 2 confirmed VAT rate/effective date, consumer advertising oversight, misleading advertising, price display, privacy/direct mailing, spam-law risk, accessibility, health advertising, environmental claims, minors, sponsored content, financial-sector advertising risk, language terminology, Tax Authority API context, and webhook non-applicability.

## [1.3.1] - 2026-06-03

### Added
- Added neutral branding audit report and Hebrew QA log.
- Added installable `advertising_campaign_planner` package for direct imports.
- Added create/show CLI chain with persisted local state and returned `plan_id`.
- Added example scripts that read environment variables, accept `--env sandbox|production`, and print UTF-8 JSON.

### Changed
- Moved client implementation out of the hyphenated script path and into the installable underscore module.
- Updated README install commands to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Hebrew public guidance to use DD/MM/YYYY dates and more natural Israeli professional terminology.
- Added `pytest-asyncio` to development requirements.

### Fixed
- Removed generated cache files from the package bundle.
- Rechecked public Markdown for emojis, decorative image links, and creator/branding tokens.

## [1.3.0] - 2026-06-03

### Added
- English and Hebrew campaign planning guides for Israeli small businesses and freelancers.
- Hebrew, Arabic, Russian, and English localization guidance.
- Israeli compliance reference for consumer protection, privacy, accessibility, spam/direct marketing, VAT-sensitive price display, regulated claims, sponsored content, and promotions.
- ROI estimator with break-even CPA and gross-profit interpretation.
- Typed Python client with synchronous and asynchronous APIs.
- Typer CLI with `plan`, `estimate-roi`, `validate`, and `template` commands.
- Pytest suite with more than 20 passing tests.
- Runnable examples for local service, ecommerce, clinic, freelancer, multilingual city, and ROI workflows.
- Troubleshooting, test scenario, workflow, and migration references.

### Changed
- Replaced promotional wording with neutral imperative guidance.
- Removed non-neutral metadata and visual asset references.
- Localized Israeli currency and date handling.
