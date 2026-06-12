# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows semantic versioning.



## [2.2.0] - 2026-06-04

### Added

- Added `references/verification-log.md` with a two-pass web validation table and summary counts.
- Added web-validated Israeli constants to `SKILL.md`, `SKILL_HE.md`, and `references/api-reference.md`.
- Added Israel Invoices 2026 threshold guidance: ₪10,000 before VAT from 01/01/2026 and ₪5,000 before VAT from 01/06/2026.
- Added Bank of Israel production data-host guidance using `edge.boi.gov.il`.
- Added a no-webhook-events note because no supplier webhook integration exists in this package.

### Changed

- Updated deterministic FX defaults to Bank of Israel representative sample rates observed in the validation pass: USD/ILS 2.8720, EUR/ILS 3.3365, GBP/ILS 3.8629.
- Updated English and Hebrew examples that previously used EUR/ILS 3.3365 calculations from old sample values.
- Clarified that Bank of Israel representative rates are indicative and not mandatory transaction settlement rates.
- Clarified that GTFS is static public-transport data and SIRI is a real-time public-transport interface class.
- Clarified Ramon Airport’s distance from Eilat and retained the transfer warning.
- Clarified that Israeli passport and destination-entry rules must be rechecked against official sources, including temporary foreign-passport exceptions.
- Clarified accessibility handling at airports: airlines or ground handlers provide passenger assistance while the airport provides infrastructure.
- Clarified tourism/hotel support: use Ministry of Tourism sources for hotel database and complaint routing, not as live room-availability APIs.

### Pass 1 findings

- Israel Tax Authority VAT history confirmed that VAT rose to 18% on 01/01/2025.
- Bank of Israel exchange-rate page confirmed representative rates and current sample values.
- Ministry of Transport GTFS page confirmed static public-transport data.
- Ministry of Transport SIRI page confirmed real-time data interface classes.
- Israel Rail official site confirmed rail schedules and trip planning role.
- Israel Airports Authority confirmed Ramon Airport location and Ben Gurion terminal structure.
- Population and Immigration Authority pages confirmed passport-validity prompts.
- Consumer Protection pages confirmed remote tourism cancellation topic coverage.
- Airport accessibility pages confirmed passenger-assistance responsibilities.
- Ministry of Tourism pages confirmed hotel database and tourism complaint sources.

### Pass 2 findings

- Tax terminology and Knesset sources reconfirmed the VAT rate.
- Israel Invoices official and govextra sources corrected 2026 allocation thresholds to the current June 2026 threshold.
- Bank of Israel explanatory notes reconfirmed publication timing and non-obligatory status of representative rates.
- Bank of Israel new-site documentation reconfirmed official data access through the series database.
- Airport and airline official pages reconfirmed Ramon domestic-flight relevance.
- Passport Q&A and embassy sources reconfirmed passport-validity cautions and the temporary foreign-passport exception.
- Accessibility cross-checks at Ben Gurion and Ramon reconfirmed assistance handling.
- Consumer cancellation cross-checks reconfirmed that cancellation rights depend on transaction type and channel.

### Removed

- Removed stale sample FX figures from user-facing examples.

## [2.1.0] - 04/06/2026

### Added

- Added a neutral packaging audit report.
- Added a Hebrew QA log.
- Added an installable `travel_booking_assistant` Python package.
- Added request creation and quote chaining through request IDs.
- Added example scripts that accept `--env sandbox|production` and read environment variables.

### Changed

- Moved the real client implementation into the underscored package module.
- Updated README installation to `pip install -e .` plus development requirements.
- Updated Israeli-facing dates to DD/MM/YYYY.
- Updated tests to import the installed package directly.
- Updated CLI to expose `create-request`, `quote`, `fx`, invoice, cancellation, and duplicate-charge helpers.

### Removed

- Removed the hyphenated client implementation file.
- Removed path-based import loading from tests and examples.


## [2.0.0] - 04/06/2026

### Added

- Comprehensive English `SKILL.md` with concrete examples, edge cases, Mermaid decision trees, anti-patterns, and production checklist.
- Full Hebrew `SKILL_HE.md` localized for Israeli business and consumer travel workflows.
- Israeli API and regulatory reference with request/response examples and error tables.
- End-to-end workflow guide.
- Troubleshooting guide with escalation templates.
- Test scenario catalog with 30 concrete scenarios.
- Migration checklist for upgrading from older skills or manual workflows.
- Typed sync and async Python client.
- Typer CLI for quote creation, FX conversion, validation, and supplier messages.
- Pytest suite with more than 20 tests.
- Runnable example scripts.
- MIT license.
- Python project metadata and development requirements.

### Changed

- Removed promotional references, visual marks, image references, and personal attribution metadata.
- Changed voice to neutral imperative guidance.
- Standardized Israeli-facing dates as DD/MM/YYYY.
- Standardized Israeli base currency as ₪ / ILS.
- Expanded domestic travel handling for Eilat, Ramon Airport, Israel Rail, local hotels, and VAT invoice prompts.
- Expanded outbound international handling for foreign currency, card markup, passport prompts, baggage, local taxes, and separate-ticket risk.
