# Changelog

## [2.2.0] - 2026-06-03

### Added

- Web-validated `references/verification-log.md` with two-pass source validation, snippets, URLs, access dates, and summary counts.
- Explicit 2026 validation note confirming Israeli VAT at 18% and routing VAT-related complaints to accounting or consumer-protection review.
- Clarification that TikTok comment monitoring is scope-dependent and must use approved Research API, TikTok API for Business where applicable, approved vendors, or permitted exports.
- Verification rows for Israeli privacy, data-security, direct-marketing, consumer-protection, defamation, copyright, accessibility, Meta, X, TikTok, Google Business Profile, brand-mention, and social-listening claims.

### Changed

- Updated metadata version to 2.2.0.
- Added current API endpoint wording for X recent search.
- Added stronger wording for news-comment limitations and source-context uncertainty.

### Validation

- Pass 1 and Pass 2 completed for 28 checks.
- Double-confirmed checks: 28.
- Corrected in Pass 2: 0.
- Final unconfirmed checks: 0.

## [2.1.0] - 2026-06-03

### Added

- Branding and public-Markdown audit report.
- Hebrew quality-assurance log.
- Installable `brand_reputation_monitor` package.
- Local configuration creation flow with an `id` that can be reused by later CLI commands.
- Environment-aware runnable examples.

### Changed

- Replaced DD/MM/YYYY references with DD/MM/YYYY localization.
- Moved the real client implementation to underscore-based module paths.
- Reworked README installation and quick-start instructions.
- Updated tests to verify package imports and chained CLI configuration.

### Removed

- Hyphenated client implementation file.
- Path-based import hacks from tests and examples.

All notable changes to this package are documented here.

The format follows Keep a Changelog, and the package uses semantic versioning.

## [2.0.0] - 2026-06-03

### Added

- Comprehensive English guide with decision trees, examples, edge cases, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew guide using natural Israeli professional terminology and ₪/DD/MM/YYYY localization.
- API and Israeli regulation reference covering privacy, data security, consumer protection, spam, defamation, copyright, accessibility, tax/accounting terms, and source patterns.
- End-to-end workflow guide.
- Troubleshooting guide.
- 40 concrete test scenarios.
- Migration checklist.
- Typed sync/async Python helper.
- Full CLI helper.
- Pytest suite with more than 20 tests.
- Five runnable example scripts.
- README, MIT LICENSE, pyproject, requirements-dev.

### Changed

- Removed branding, visual identity references, distribution callouts, and author metadata.
- Reworked tone into neutral imperative guidance.
- Expanded tags and package metadata.

### Security

- Added privacy redaction for email addresses, Israeli phone numbers, and 9-digit ID-like patterns.
- Added urgent escalation guidance for safety, privacy, legal, media, and regulator-related mentions.
