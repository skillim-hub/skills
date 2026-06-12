# Changelog

## [1.3.0] - 2026-06-03

### Web validation
- Double-confirmed that Israeli VAT is 18% from 01/01/2025 and remains the active documented rate in 2026.
- Double-confirmed Hebrew regulatory terminology for מע"מ, דבר פרסומת, דיוור ישיר, נגישות, תקן ישראלי 5568, and WCAG 2.0.
- Double-confirmed consent, opt-out, privacy, database-registration, accessibility, and consumer-protection guidance against misleading or fabricated reviews.
- Double-confirmed WhatsApp customer-service-window guidance, template messaging outside the window, webhook status/inbound-message coverage, and current Graph API version availability.
- Double-confirmed Twilio endpoint, status-callback fields, message-status values, Hebrew/Unicode SMS considerations, and Israel sender constraints.
- Double-confirmed SendGrid Mail Send endpoint behavior, 202 Accepted response semantics, and EU subuser host option.
- Double-confirmed Google Maps URL parameters `api=1` and `query_place_id`, Google Business Profile review-management API capabilities, and quota/error handling.
- Double-confirmed Zap, Easy, Midrag, and B144 as Israeli profile or review destinations where verified profile URLs should be tested before campaigns.
- Could not confirm public write-review submission APIs for Zap, Easy, Midrag, or B144; the package continues to treat them as destination links unless a contracted partner API is verified.
- Verified the overall skill claim by decomposing it into official channel API evidence and live Israeli rating-directory destination evidence.

### Corrected
- Updated WhatsApp Cloud API examples from `v19.0` to `v25.0`.
- Replaced the undocumented default Google write-review shortcut with the official Google Maps URL pattern using `api=1` and `query_place_id`.
- Reclassified direct Google write-review shortcuts as optional, non-default links that require manual validation and terms review.
- Updated Hebrew-visible dates to `DD/MM/YYYY` format where not part of machine-readable timestamps.
- Added `references/verification-log.md` with pass-1 and pass-2 source evidence, snippets, URLs, access dates, and status tags.

All notable changes to this package are documented in this file.

## [1.2.0] - 2026-06-03

### Changed

- Replaced hyphenated Python implementation files with import-safe underscored script entrypoints and an installable `customer_feedback_collector` package.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Changed CLI plan output to a machine-readable create response containing `plan_id`, then documented use of that identifier in the send step.
- Regenerated examples so each script reads environment variables, accepts `--env sandbox|production`, and prints JSON with `ensure_ascii=False` and `indent=2`.
- Updated Hebrew documentation terminology and localization to use ₪ and DD/MM/YYYY formatting.

### Added

- Added `references/branding-audit.md` with hard branding, attribution, visual-asset, and emoji audit results.
- Added `references/hebrew-qa-log.md` with Hebrew QA changes.
- Added `pytest-asyncio` to development requirements.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [1.1.0] - 2026-06-03

### Added

- Added neutral customer-feedback collector skill for Israeli review and testimonial workflows.
- Added English and Hebrew guides with decision trees, examples, troubleshooting, anti-patterns, edge cases, and production checklists.
- Added API and regulation reference covering WhatsApp Cloud API, SMS providers, email providers, Google review links, Facebook reviews, Israeli directory platforms, privacy, anti-spam, accessibility, and consumer-protection guardrails.
- Added end-to-end workflow guide for post-service WhatsApp, ecommerce email, SMS fallback, testimonial approvals, detractor routing, and quarterly cleanups.
- Added dedicated troubleshooting, test scenarios, and migration checklist references.
- Added typed Python client with synchronous and asynchronous planning/sending helpers.
- Added Typer CLI for sample messages, validation, campaign planning, safe-time calculation, and dry-run sending.
- Added pytest suite with more than 20 unit and CLI tests.
- Added runnable examples for WhatsApp, SMS, email, private feedback routing, and bulk CSV planning.
- Added pyproject and development requirements.

### Changed

- Renamed and refocused the package around customer feedback, public reviews, and testimonials rather than survey construction.
- Localized Hebrew output for Israeli business usage, including ₪ examples and DD/MM/YYYY dates.

### Removed

- Removed author metadata.
- Removed promotional, organizational, and visual identity references.
