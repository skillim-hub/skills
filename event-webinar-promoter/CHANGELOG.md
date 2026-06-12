# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows Semantic Versioning.

## [2.2.0] - 2026-06-03

### Added

- Web-validated `references/verification-log.md` with Pass 1 and Pass 2 source columns.
- Current checked VAT value: 18%, effective 01/01/2025.
- Current checked 2026 exempt-dealer turnover ceiling: ₪122,833.
- Official terminology table for direct marketing, privacy, accessibility, VAT, and invoice allocation.
- Mass/public event licensing caution for events that may require local authority review.

### Changed

- Clarified that Israeli website accessibility checks should use Israeli Standard 5568 / WCAG 2.0 level AA.
- Clarified that Tax Authority invoice allocation API details are not called by this package.
- Bumped metadata version to 2.2.0.

### Verification findings

- Pass 1 confirmed VAT 18%, direct marketing opt-out terminology, privacy Amendment 13, accessibility-event obligations, website accessibility terminology, consumer cancellation context, Tax Authority invoice allocation service topic, IANA timezone source, WhatsApp `wa.me`, UTM parameters, and iCalendar VEVENT/TZID basis.
- Pass 2 independently confirmed the same rows or found no package-level correction needed.
- One exact marketing-description search did not produce an official source; the component claims are validated separately in the verification log.

## [2.1.0] - 2026-06-03

### Added

- Branding audit report in `references/branding-audit.md`.
- Hebrew QA log in `references/hebrew-qa-log.md`.
- Installable package module `event_webinar_promoter`.
- Stored event workflow with `create` response and reusable `event_id`.
- Console entry point `event-webinar-promoter`.
- Compile-time syntax verification step.

### Changed

- Replaced hyphenated client path with underscored `scripts/event_webinar_promoter_client.py`.
- Updated README installation to `pip install -e .` and development requirements installation.
- Updated quick start to chain `create` response extraction into the next command.
- Updated examples to accept `--env sandbox|production`, read environment variables, and emit JSON with `ensure_ascii=False`.
- Updated Hebrew-facing documentation and generated copy to use `DD/MM/YYYY`.

### Fixed

- Removed residual blocked branding placeholder from migration guidance.
- Removed path-based import hacks from tests.
- Confirmed public Markdown contains no emoji, visual identity asset URLs or image references.

## [2.0.0] - 2026-06-03

### Added

- Comprehensive English guide in `SKILL.md`.
- Full Hebrew guide in `SKILL_HE.md` with natural Israeli professional terminology.
- Israeli regulation and API-equivalent reference in `references/api-reference.md`.
- End-to-end workflows in `references/workflow-guide.md`.
- Troubleshooting playbook in `references/troubleshooting.md`.
- 30 concrete test scenarios in `references/test-scenarios.md`.
- Migration checklist in `references/migration-checklist.md`.
- Typed sync/async Python helper in `scripts/event-webinar-promoter-client.py`.
- Click CLI in `scripts/event-webinar-promoter-cli.py`.
- Pytest suite with more than 20 tests.
- Six runnable scenario examples.
- MIT license.
- Project configuration and development requirements.

### Changed

- Bumped package version to `2.0.0`.
- Expanded metadata tags for Israeli event/webinar campaign planning.
- Standardized Israel timezone handling with `Asia/Jerusalem`.
- Standardized Hebrew-facing dates to `DD-MM-YYYY`.
- Standardized pricing to ₪.
- Converted guidance to neutral imperative voice.

### Removed

- Creator metadata.
- Branding references.
- Visual identity assets and distribution callouts.
- Any dependency on external network calls for planning.

### Security

- Added operational checks for consent, unsubscribe, registration data minimization, privacy note, partner list handling, and secure event data handling.

## [1.0.0] - 2026-06-03

### Added

- Initial minimal package.
