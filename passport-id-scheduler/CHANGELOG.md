# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses Semantic Versioning.

## [2.2.0] - 2026-06-02

### Added
- Added `references/verification-log.md` with two-pass web validation, source URLs, access date, and short official-source quotations.
- Added VAT verification note for business users while keeping VAT outside appointment booking.

### Changed
- Updated official appointment channel references from legacy appointment host to GoVisit after pass 1 and pass 2 validation.
- Updated public-source references from non-official legal database links to gov.il or Knesset National Legislation Database pages where available.
- Updated Hebrew wording and currency examples to avoid hard-coded fee impressions.
- Bumped package metadata and Python project version to 2.2.0.

### Fixed
- Corrected CLI production default, client official-host hints, tests, examples, and metadata tags to use `govisit.gov.il`.
- Marked local endpoint paths as wrapper examples only, not official government API contracts.

### Verification findings
- Pass 1 confirmed GoVisit as the current appointment channel and identified legacy legacy appointment host references in the package.
- Pass 2 confirmed Population and Immigration Authority appointment categories on GoVisit and gov.il English/Hebrew service pages.
- Double-confirmed biometric passport/ID appointment wording, passport and identity-card service terminology, online biometric ID cases, activation, ID appendix, address update, fees table, VAT rate, privacy-law terminology, and law-reference sources.
- Could not confirm any official public appointment-booking API or webhook contract; the package remains a local helper only.

## [2.1.0] - 2026-06-02

### Changed
- Replaced hyphenated Python module filenames with importable underscored modules.
- Updated installation instructions to use editable install plus development requirements.
- Added request-record commands so quick-start examples pass a returned id to a follow-up command.
- Updated examples to read environment variables, accept `--env sandbox|production`, and emit UTF-8 JSON.
- Updated Hebrew localization to use neutral imperative language, Israeli terminology, and `DD/MM/YYYY` display dates.

### Added
- Added branding and visual-asset audit report.
- Added Hebrew QA log.

### Fixed
- Added `pytest-asyncio` to development requirements.
- Made the client module importable after `pip install -e .`.

## [2.0.0] - 2026-06-02

### Added
- Complete Passport & ID Appointment Scheduler scope.
- English and Hebrew skill guides.
- Public source, regulation, and local interface reference.
- Workflow guide for passport, ID, minor, urgent, family, business, address, accessibility, and name/status cases.
- Troubleshooting guide.
- Test scenario reference with more than 20 concrete scenarios.
- Migration checklist.
- Typed sync and async Python client.
- Typer CLI.
- pytest suite with more than 20 tests.
- Runnable example scripts.
- MIT license, pyproject, and development requirements.

### Changed
- Shifted from generic form automation to official-channel appointment preparation.
- Added safety boundaries for CAPTCHA, queues, credentials, OTPs, and payment data.
- Localized Hebrew guidance with Israeli date and currency formatting.

### Removed
- Branding.
- Contributor metadata.
- Visual assets, visual references, and distribution callouts.
- Unrelated tax, National Insurance, and company-registration form workflows.
