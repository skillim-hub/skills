# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added two-pass web verification log at `references/verification-log.md` with source snippets, URLs, access date, status tags, and a summary table.
- Added official form and endpoint references for serious breach reporting and database registration.
- Added helper functions for medium-security triggers, Amendment 13 registration review, Amendment 13 notification review, and DPO review.

### Changed

- Corrected Israeli data-security level logic against official Privacy Protection Authority sources: medium level now follows public-body, data-broker/direct-mailing-service, or special-sensitivity triggers.
- Corrected high-security logic to require a medium-level trigger plus 100,000 or more people or more than 100 authorized users.
- Removed the previous generic 10,000-person and 10-user medium-security trigger from code, tests, English guidance, Hebrew guidance, troubleshooting, and scenario references.
- Updated clinic guidance to distinguish statutory medium security from higher practical operational severity for health data.
- Updated Amendment 13 guidance for database registration, authority notification, DPO review, and regulator-facing evidence.
- Added a VAT validation note clarifying that VAT is business context only and is not calculated by the privacy helper.

### Fixed

- Fixed scenario tests and async persistence assertions to match the corrected security-level thresholds.
- Replaced the script-level client duplicate with an import shim to avoid implementation drift.

## [2.1.0] - 2026-06-02

### Added

- Added installable `privacy_compliance_checker` Python package.
- Added source-tree underscored client module.
- Added source-tree command entry point.
- Added audit report at `references/branding-audit.md`.
- Added Hebrew QA log at `references/hebrew-qa-log.md`.
- Added full CLI state workflow: create, get, update, list, delete, assess, validate, checklist, scenarios, and template.
- Added pytest coverage for sync client, async client, CLI, persistence, GDPR checks, transfer checks, breach checks, and package imports.
- Added `pytest-asyncio` to development requirements.
- Added example scripts with environment handling and formatted Unicode JSON output.

### Changed

- Bumped metadata version.
- Updated README installation to use editable package installation plus development requirements.
- Updated quick-start flow to extract an assessment ID from the create response and reuse it in the next command.
- Reworked Hebrew guidance for neutral imperative language, Israeli professional terminology, ₪ currency examples, and DD/MM/YYYY date format.
- Reworked package structure so `from privacy_compliance_checker import ...` works after installation.
- Updated public Markdown to remove decorative icons and image or visual asset references.

### Removed

- Removed hyphenated Python implementation files from `scripts/`.
- Removed attribution metadata.
- Removed public branding, visual asset, visual asset and image references.

## [2.0.0] - 2026-06-02

### Added

- Added comprehensive English and Hebrew skill guides.
- Added workflow guide, troubleshooting reference, test scenarios, migration checklist, README, license, and development configuration.
- Added deterministic compliance client and CLI helper.
- Added five runnable examples.

### Changed

- Expanded privacy checks for Israeli small businesses, freelancers, consumers, and lightweight cloud-service workflows.
- Added GDPR, direct marketing, cross-border transfer, processor, breach, retention, rights, and production-readiness checks.

## [1.0.0] - 2026-06-02

### Added

- Initial privacy compliance checker package.
