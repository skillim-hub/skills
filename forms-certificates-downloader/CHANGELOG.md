# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, short source snippets, URLs, access date, status tags, and summary counts.
- Added `bituach-leumi-certificates` as a separate public certificate-information source.
- Added tests that assert the web-validated default registry URLs.
- Added migration guidance from 2.1.0 to 2.2.0.

### Changed

- Pass 1 finding: confirmed VAT increased to 18% on 01/01/2025 from the Tax Authority VAT history page.
- Pass 2 finding: confirmed the 18% VAT rate remains current in 2026 from an independent 2026 tax reference and the Knesset effective-date notice.
- Pass 1 finding: the Tax Authority Hebrew department URL resolves as `israel_tax_authority` without the older `govil-landing-page` suffix.
- Pass 2 finding: the English Tax Authority department page confirms the same authority terminology.
- Pass 1 finding: the income-tax topic URL is `income_tax_israel_tax_authority` and lists annual tax-report services.
- Pass 2 finding: the English income-tax topic page confirms the same topic.
- Pass 1 finding: Bituach Leumi forms should use the dedicated `/forms/Pages/default.aspx` category page.
- Pass 2 finding: the English National Insurance forms page confirms that forms are available in PDF format.
- Pass 1 finding: National Insurance certificates have a separate public information page.
- Pass 2 finding: the broader National Insurance forms-and-certificates page confirms personal-service printing boundaries.
- Pass 1 finding: the gov.il services index is plural `/he/services`.
- Pass 2 finding: broader gov.il search and subject pages confirm the general services-and-information model.
- Pass 1 finding: Corporations Authority gov.il page should use `israeli_corporations_authority`.
- Pass 2 finding: the Corporations Online site confirms the official English terminology and public-information boundary.

### Fixed

- Corrected stale registry URLs for Tax Authority, income-tax topic, gov.il services, and Corporations Authority.
- Updated README, skill guides, API reference, workflow guide, troubleshooting guide, package registry, hardcoded fallback registry, examples, and tests to match the corrected sources.
- Avoided hard-coding dynamic gov.il service counts.

## [2.1.0] - 2026-06-02

### Added

- Added installable `forms_certificates_downloader` Python package.
- Added saved download request workflow with `create-request` and `run-request`.
- Added package console command `forms-certificates-downloader`.
- Added branding audit report and Hebrew QA log.
- Added `pytest-asyncio` to development requirements.
- Added environment-aware examples with `--env sandbox|production`.

### Changed

- Moved public imports away from hyphenated Python file names.
- Updated README installation to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to extract `request_id` from create response and reuse it.
- Updated examples to read environment variables and emit JSON with `ensure_ascii=False`.
- Expanded Hebrew guidance with Israeli professional terminology and DD/MM/YYYY localization.

### Removed

- Removed hyphenated client and CLI Python files.
- Removed path-loading import patterns from tests and examples.
- Removed decorative public Markdown artifacts and image-style references.

## [2.0.0] - 2026-06-02

### Added

- Added bilingual skill documentation.
- Added typed sync and async client.
- Added CLI.
- Added reference guides, troubleshooting, test scenarios, migration checklist, examples, and tests.
- Added neutral MIT license.
