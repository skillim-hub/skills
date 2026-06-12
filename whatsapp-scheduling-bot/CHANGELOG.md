# Changelog

All notable changes to this skill package are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning.

## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation across official Israeli, Meta, WhatsApp, and supporting API sources.
- Added web-validated defaults for Graph API version, WhatsApp pricing model, Hebrew template language, Israeli VAT display, and compliance terminology.

### Changed

- Updated default Graph API version from `v20.0` to `v25.0` in client, CLI, examples, and documentation after checking Meta Graph API version listings twice.
- Reworded WhatsApp market-positioning claims from absolute "main"/"standard" language to "common customer-service channel" language.
- Reworded pricing guidance from conversation-cost language to delivered-message, market/category-based pricing.
- Updated the status webhook pricing example to use per-message pricing fields and note older/free-entry variants.
- Added Israeli VAT guidance for `18%` from `01/01/2025`, with no automatic tax calculation unless explicitly required.

### Verified

- Double-confirmed Israeli VAT, WhatsApp Cloud API official status, send-message endpoint, webhook field, status names, template language `he`, section 30A anti-spam terms, privacy/data-security terminology, consumer cancellation references, data.gov.il CKAN API, and Israeli `+972` numbering.
- Corrected API version, pricing-model wording, and overbroad WhatsApp-channel positioning during Pass 2.

## [2.1.0] - 2026-06-03

### Added

- Comprehensive English scheduling guide.
- Full Hebrew guide with Israeli professional terminology, ₪ prices, and `DD/MM/YYYY` dates.
- WhatsApp API and Israeli regulation reference with request/response examples.
- Workflow guide for booking, reminders, rescheduling, cancellations, no-shows, waiting lists, escalation, import, opt-out, and daily review.
- Troubleshooting guide with recovery playbooks.
- 40 concrete test scenarios.
- Migration checklist for manual WhatsApp, spreadsheets, booking tools, and provider migration.
- Typed synchronous and asynchronous Python client.
- Typer-based CLI helper.
- Five runnable examples.
- Pytest suite with 38 tests.
- Pyproject configuration and development requirements.
- README and MIT license.

### Changed

- Refocused the package from generic WhatsApp Business integration to Hebrew appointment booking and reminders for Israeli service businesses.
- Updated metadata version to `2.1.0`.
- Expanded tags for scheduling, reminders, booking, privacy, and Israeli localization.
- Reworked wording into neutral imperative guidance.

### Removed

- Removed attribution metadata.
- Removed organization-specific branding.
- Removed decorative media references.
- Removed distribution callouts.
