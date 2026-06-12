# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [0.4.0] - 2026-06-04

### Added

- `references/verification-log.md` with two-pass web validation, snippets, URLs, access date, and a summary table.
- VAT reference note confirming the Israel Tax Authority's 18% VAT rate from 01/01/2025.
- Google Business Profile review reply state reference for `PENDING`, `REJECTED`, and `APPROVED`.

### Changed

- Updated WhatsApp Cloud API examples to use `<API_VERSION>/<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/messages` instead of a hardcoded Graph API version.
- Updated the Google Business Profile review reply example to the official `updateReply` gRPC-transcoding path.
- Clarified that SMS and CRM webhook endpoint examples are illustrative and must be replaced with the selected provider's documented endpoint.

### Web validation findings

- Pass 1 and Pass 2 double-confirmed: VAT rate, VAT transition date, spam-law framing, privacy consent, data security, consumer protection, accessibility, electronic-signature terminology, WhatsApp customer-service window, WhatsApp webhook categories, Google Business Profile federated API model, review list/get/reply/delete operations, Google review fake-engagement policy, neutral non-incentivized review solicitation, and Google review reply state fields.
- Corrected after validation: WhatsApp endpoint versioning and Google review reply endpoint path.
- Not externally confirmable: the package-specific description sentence, the generic SMS gateway example, and the generic CRM webhook example.


## [0.3.0] - 2026-06-04

### Added

- Deep verification reports for restricted identifiers, image references, public Markdown cleanup, and Hebrew quality review.
- Installable Python package under `followup_review_solicitor`.
- Request creation workflow with saved request IDs for command line chaining.
- Environment-aware runnable examples with `--env sandbox|production`.

### Changed

- Replaced the hyphenated client implementation with an underscored import surface.
- Updated public localization to `DD/MM/YYYY`.
- Updated README installation to use editable package installation plus development requirements.
- Updated tests to import the installable package directly.

### Fixed

- Removed path-based import loading from examples and tests.
- Added `pytest-asyncio` to development requirements.
- Added syntax verification with `compileall`.


## [0.2.0] - 2026-06-04

### Added

- Comprehensive English skill guide with decision tree, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- Full Hebrew guide with Israeli terminology, ₪ formatting, and `DD/MM/YYYY` localization.
- API and regulation reference with channel payloads, response examples, and error tables.
- End-to-end workflow guide for home services, freelancers, accountants, payments, delivery, appointments, consumers, branches, approval queues, and CSV previews.
- Troubleshooting guide for message quality, timing, consent, channel, and migration failures.
- Test scenario catalog with 30 concrete scenarios.
- Migration checklist for replacing manual, spreadsheet, or legacy CRM follow-up processes.
- Typed sync and async Python helper.
- Typer CLI for generating plans and validating phone numbers.
- Pytest suite with more than 20 tests.
- Five runnable example scripts.
- MIT license, pyproject configuration, and development requirements.

### Changed

- Expanded metadata tags and bumped version from `0.1.0` to `0.2.0`.
- Replaced stub content with production-oriented guidance.
- Removed non-neutral distribution language.

### Security

- Added consent, opt-out, sensitive-context, idempotency, and provider-secret controls.
