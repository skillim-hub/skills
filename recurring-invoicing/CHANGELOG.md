# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [1.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, official snippets, URLs, access date, statuses, and summary counts.
- Added date-effective allocation threshold support through `threshold_for_issue_date`.
- Added tests for the 01/01/2026 and 01/06/2026 threshold transitions.

### Changed

- Updated documentation to state that 2026 allocation thresholds are ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026.
- Clarified that local allocation helper payloads require adapter mapping to the official lowercase SHAAM v2 schema before direct Tax Authority submission.
- Updated API reference with verified approval endpoints, retrieval endpoints, manual service requirements, error handling, and held-invoice alternatives.
- Updated Hebrew guide with current 2026 terminology, DD/MM/YYYY dates, and no nikud in technical prose.

### Fixed

- Corrected the stale full-year 2026 allocation threshold of ₪15,000 found in older API materials.
- Avoided hard-coding the held-invoice decision-service endpoint because public English and Hebrew PDFs conflict on the path.
- Replaced duplicated script client implementation with a compatibility wrapper to prevent stale copies.

### Web validation findings

- Pass 1 confirmed the VAT transition to 18 percent from 01/01/2025.
- Pass 2 confirmed the VAT rate against a 2026-reviewed professional tax summary.
- Pass 1 found the older API-document schedule showing ₪15,000 for 2026.
- Pass 2 corrected the threshold using updated Tax Authority service pages showing ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026.
- Pass 1 and Pass 2 confirmed the approval v2 sandbox and production endpoint paths.
- Pass 1 and Pass 2 confirmed OAuth2 User Restricted authorization and lowercase v2 input fields.
- Pass 1 and Pass 2 found conflicting public paths for the held-invoice decision service, so production adapters must verify that path in the developer portal.

## [1.1.0] - 2026-06-02

### Added

- Added installable `recurring_invoicing` package with normal imports.
- Added underscored script files and removed hyphenated client usage.
- Added branding audit report and Hebrew QA log.
- Added examples that read environment variables, accept `--env sandbox|production`, and print JSON using `ensure_ascii=False`.
- Added compile check requirement and expanded test coverage.

### Changed

- Revised README install flow to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start to extract the subscription ID from the create response before the next step.
- Updated public Markdown to remove emoji, visual assets, and promotional wording.
- Revised Hebrew documentation for natural Israeli terminology, neutral imperative voice, and `DD/MM/YYYY` date formatting.

### Fixed

- Removed hyphenated client import pattern and dynamic module loading.
- Ensured `pytest-asyncio` is listed in development requirements.
- Configured package discovery so `from recurring_invoicing import ...` works after editable installation.

## [1.0.0] - 2026-06-02

### Added

- Initial enhanced package with English and Hebrew guides.
- Added API reference, workflow guide, troubleshooting guide, test scenarios, migration checklist, CLI, examples, tests, and MIT license.
