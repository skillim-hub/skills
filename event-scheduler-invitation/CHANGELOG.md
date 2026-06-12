# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-04

### Added
- Added `references/verification-log.md` with two-pass web validation, source URLs, access date, short snippets, status tags, and summary counts.
- Added 2026 Tax Authority invoice allocation thresholds: ₪10,000 before VAT from 01/01/2026 and ₪5,000 before VAT from 01/06/2026.
- Added VAT planning constant at 18% and `tax_documentation_check()` for supplier/customer invoice follow-up.
- Added ACUM family-event planning fee reference of ₪395.30 including VAT, 72-hour buffer, and `music_license_checkpoint()`.
- Added CLI commands `tax-check` and `music-license`.
- Added scenario coverage for invoice thresholds, ACUM family/business separation, and venue noise-monitor checks.

### Changed
- Corrected older Israel Invoices API threshold assumptions after Pass 2 found current Tax Authority service pages supersede the older API PDF.
- Updated English and Hebrew guides with web-validated VAT, invoice allocation, ACUM, noise-monitor, and brit milah fee checkpoints.
- Updated workflow, troubleshooting, migration, examples, and tests to use current 2026 operational checks.
- Kept WhatsApp provider webhook status names separate from internal RSVP status values.

### Verified
- Pass 1 checked official or live sources for VAT, invoice allocation, ACUM, communications law, privacy, accessibility, noise, marriage registration, kashrut, brit milah, WhatsApp webhooks, timezone, and Israeli RSVP market fit.
- Pass 2 rechecked confirmed rows with different pages or sources where possible.
- Final status: 22 double-confirmed rows, 1 corrected-in-pass-2 row, 0 final unconfirmed rows.

## [2.1.0] - 2026-06-04

### Added
- Added `references/branding-audit.md` with a full branding, author-neutrality, visual-asset, and public-Markdown emoji audit.
- Added `references/hebrew-qa-log.md` with Hebrew terminology, date-format, and voice corrections.
- Added installable `event_scheduler_invitation` package so `from event_scheduler_invitation import ...` works after `pip install -e .`.
- Added chainable CLI `create-plan` response with `event_id` and `add-guest` command that validates the event identifier.
- Added underscored script client at `scripts/event_scheduler_invitation_client.py`.
- Added runnable examples that accept `--env sandbox|production`, read environment variables, and print JSON with `ensure_ascii=False`.

### Changed
- Changed Hebrew-facing date localization to `DD/MM/YYYY` while keeping parsers backward compatible with `DD/MM/YYYY` and ISO dates.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated tests to import the package without file-path import hacks.
- Updated public Markdown to remove emoji and avoid visual-asset, author and distribution references.
- Replaced Hebrew terminology where a standard Israeli professional term is preferable.

### Removed
- Removed the hyphenated client file `scripts/event-scheduler-invitation-client.py`.
- Removed path-based client loading from README and CLI code.

## [2.0.0] - 2026-06-04

### Added
- Added bilingual English and Hebrew operating guides for Israeli lifecycle event planning.
- Added Israeli API and regulation reference, workflow guide, troubleshooting guide, test scenarios, migration checklist, README, LICENSE, pyproject, and development requirements.
- Added typed synchronous and asynchronous Python helper, CLI, runnable examples, and pytest coverage.

### Changed
- Expanded scope from wedding-only planning to weddings, bar mitzvah, bat mitzvah, brit milah, family events, community events, customer events, and small-business events.
- Localized budgeting, RSVP messaging, guest handling, supplier workflows, and venue logistics for Israeli use.

## [1.0.0] - 2026-06-04

### Added
- Initial event scheduling and invitation management package.
