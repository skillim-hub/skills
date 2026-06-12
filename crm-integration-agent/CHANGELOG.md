# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.


## [1.3.0] - 2026-06-04

### Changed

- Added two-pass web validation for Israeli VAT, privacy, direct marketing, spam, Monday, HubSpot, Salesforce, Meta WhatsApp, Twilio SMS, and SendGrid Inbound Parse references.
- Updated HubSpot Contacts API path from `/crm/v3/objects/contacts` to `/crm/objects/2026-03/contacts` after pass-2 validation.
- Updated Salesforce default REST API version from `v59.0` to configurable `v67.0` after pass-2 validation.
- Added `references/verification-log.md` with source snippets, URLs, access date, and correction status.
- Updated README, API reference, English guide, Hebrew guide, tests, and examples to reflect validated API defaults.

### Fixed

- Replaced runnable examples that attempted to serialize slotted dataclasses through `__dict__`; examples now use `result_to_dict`.
- Removed a duplicated Hebrew channel alias from the client.

## [1.2.0] - 2026-06-04

### Added

- Added installable `crm_integration_agent` package with package-level imports.
- Added branding and creator audit report.
- Added Hebrew QA log.
- Added environment-aware examples with `--env sandbox|production`.
- Added create-response id chaining guidance in README.
- Added audit-template option for passing a CRM object id.

### Changed

- Replaced hyphenated Python files with underscored wrappers.
- Updated localized date handling to DD/MM/YYYY.
- Updated development install instructions to use editable install and development requirements.
- Expanded tests for package imports, environment handling, localized timestamps, and id extraction.

### Removed

- Removed dynamic import shims that depended on hyphenated filenames.
- Removed public Markdown emoji, image references, and status-image references.

## [1.1.0] - 2026-06-04

### Added

- Added English and Hebrew operating guides.
- Added API reference, workflow guide, troubleshooting guide, test scenarios, and migration checklist.
- Added typed client, CLI, examples, tests, packaging files, README, and MIT license.

## [1.0.0] - 2026-06-04

### Added

- Initial neutral CRM conversation-sync skill structure.
