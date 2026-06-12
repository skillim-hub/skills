# Changelog

All notable changes to this project are documented in this file.

## [2.2.0] - 2026-06-02

### Added
- Added `references/verification-log.md` with two-pass live-source validation, source URLs, access date, short source quotes, correction status, and summary counts.
- Added validated official-source notes for VAT, Cardcom, Tranzila, Grow, Pelecard, SHVA/Ashrait, Bank of Israel payment-system context, privacy, consumer protection, and PCI DSS.

### Changed
- Corrected provider wording from a five-provider live API claim to Cardcom, Tranzila, Pelecard, and Grow, with Meshulam treated as the former Grow name or a legacy contract alias.
- Clarified that internal orchestration paths are not provider endpoint paths.
- Clarified that webhook event names are not portable across providers and must be normalized into internal statuses.
- Updated Hebrew guidance to professional Israeli terminology, neutral imperative style, `₪`, and `DD/MM/YYYY` localization.
- Bumped package metadata, Python package version, and project version to 2.2.0.

### Fixed
- Fixed README Python quick-start extraction of transaction id by reading fallback identifiers from the raw response dictionary.
- Removed unvalidated implications about universal provider webhook events.
- Reduced unverified provider field certainty where current live sources require merchant-contract validation.

## [2.1.0] - 2026-06-02

### Added

- Neutrality and public Markdown audit report.
- Hebrew terminology and localization quality-assurance log.
- Importable `payment_gateway_integrator` package under `src/`.
- Console entry point `pgi-payment`.

### Changed

- Deleted hyphenated Python script names and replaced them with underscored script entry points.
- Moved the implementation behind an installable package so `from payment_gateway_integrator import ...` works after `pip install -e .`.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick-start flow to extract a transaction id from the create response and use it in the status call.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Updated Hebrew terminology, neutral imperative wording, and local date format to `DD/MM/YYYY`.

### Fixed

- Removed generated cache artifacts from the bundle.
- Removed stale dynamic import recipes from public documentation.
- Verified public Markdown contains no emoji or visual promotional asset links.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with decision trees, edge cases, troubleshooting entry points, anti-patterns, and production checklist.
- Comprehensive Hebrew guide using Israeli professional terminology, `₪` formatting, and `DD/MM/YYYY` localization.
- API and regulation reference covering Cardcom, Tranzila, Meshulam, Pelecard, Grow, Shva, Bank of Israel, consumer protection, privacy, tax, and PCI references.
- End-to-end workflow guide for checkout, installments, subscriptions, authorization/capture, refunds, callbacks, reconciliation, outages, migration, and support.
- Dedicated troubleshooting guide.
- Dedicated test-scenarios reference with 30 concrete scenarios.
- Migration checklist for gateway replacement and multi-gateway rollout.
- Typed sync and async Python client.
- Click-based CLI.
- Pytest suite with more than 20 tests.
- Runnable examples for one-time charge, hosted checkout, refund, fallback routing, callback verification, and async charge.
- README, MIT license, pyproject, and development requirements.

### Changed

- Expanded metadata tags and bumped version to `2.0.0`.
- Reworked content into a neutral imperative voice.
- Replaced gateway comparison-only content with production orchestration patterns.

### Removed

- Creator metadata.
- Branding references.
- Visual promotional assets and image references.
