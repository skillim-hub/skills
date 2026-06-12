# Changelog

All notable changes are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.


## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with a two-pass web validation table, source URLs, access date, short snippets, and status tags.
- Added a non-applicability note for webhook event names because the skill has no webhook surface.
- Added source-backed validation for Hebrew UX/register guidance and Israeli-market copywriting positioning.

### Changed

- Updated VAT wording from baseline phrasing to current web-validated phrasing: Pass 1 confirmed the 18% rate from Israel Tax Authority terminology; Pass 2 confirmed 18% in 2026 gov.il accounting material.
- Confirmed the VAT effective date using a government decision in Pass 1 and a Knesset source in Pass 2.
- Confirmed consumer-protection guidance using the Consumer Protection Authority in Pass 1 and court/Knesset sources in Pass 2.
- Confirmed price-presentation guidance using the Consumer Protection Authority in Pass 1 and a Supreme Court source in Pass 2.
- Confirmed cancellation-timing references using a Consumer Protection Authority guide in Pass 1 and a 2026 enforcement notice in Pass 2.
- Confirmed direct-marketing and unsubscribe guidance using a gov.il spam FAQ in Pass 1 and Privacy Protection Authority material in Pass 2.
- Confirmed privacy lead-form guidance using a 2026 Privacy Protection Authority page in Pass 1 and direct-mail guidance in Pass 2.
- Confirmed data.gov.il endpoint patterns using data.gov.il documentation in Pass 1 and a CKAN API snippet in Pass 2.
- Confirmed public-dataset guidance using the data.gov.il homepage in Pass 1 and the data.gov.il about page in Pass 2.
- Confirmed company registry lookup guidance using the data.gov company dataset in Pass 1 and data.gov CKAN documentation in Pass 2.
- Confirmed accessibility guidance using Equal Rights Commission material in Pass 1 and a Knesset accessibility statement in Pass 2.
- Confirmed professional Hebrew terminology and clear-language guidance using the government language guide in Pass 1 and the Campus IL government microcopy course in Pass 2.
- Confirmed the Hebrew copywriting market-positioning claim using two public market sources in Pass 1 and Pass 2.

### Fixed

- Replaced an awkward mixed-language table label in `references/api-reference.md` with a clear English label.
- Linked the new verification log from the README and API reference.


## [2.1.0] - 2026-06-03

### Added

- Branding audit report.
- Hebrew quality assurance log.
- Installable `hebrew_copywriter` package.
- Saved-brief CLI workflow with response id chaining.
- Environment-aware runnable examples.
- Compile-all syntax validation step.

### Changed

- Switched user-facing date localization examples from hyphen-separated date format to DD/MM/YYYY.
- Replaced dynamic import shims with package imports.
- Moved client access to an underscored script module and removed the hyphenated client script.
- Updated development requirements to include `pytest-asyncio`.

### Removed

- Generated cache files from the deliverable archive.

## [2.0.0] - 2026-06-03

### Added

- Comprehensive English `SKILL.md`.
- Comprehensive Hebrew `SKILL_HE.md` with Israeli professional terminology.
- Israeli regulation and API reference covering consumer protection, spam, privacy, accessibility, VAT, public-data APIs, and examples.
- Workflow guide for landing pages, WhatsApp, SMS, מסחר מקוון, ads, nonprofit copy, quote follow-ups, and rewrites.
- Troubleshooting guide with decision flow, repairs, and scoring rubric.
- Test scenario reference with 25 concrete scenarios.
- Migration checklist.
- Typed synchronous and asynchronous helper client.
- Click-based CLI.
- Pytest suite with more than 20 tests.
- Five runnable scenario scripts.
- README, MIT license, pyproject, and development requirements.

### Changed

- Bumped version from uploaded `1.1.0` baseline to `2.0.0`.
- Refocused from general Hebrew content writing to practical Hebrew copywriting for Israeli audiences.
- Expanded localization rules for ₪, DD/MM/YYYY, VAT, direct marketing, gender, and channel-specific copy.

### Removed

- Personal attribution metadata.
- Organization attribution.
- Distribution references.
- Visual references.
