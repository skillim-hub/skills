# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.1.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, and status counts.
- Added current VAT, timezone, API endpoint, webhook, privacy, spam, consumer-protection, accessibility, open-data, and exchange-rate source checks.

### Changed

- Updated LinkedIn publishing examples from legacy `https://api.linkedin.com/rest/posts` to current `https://api.linkedin.com/rest/posts`.
- Added the required `Linkedin-Version` header to LinkedIn request examples.
- Documented TikTok Content Posting webhook event names from the status-management reference.
- Updated metadata, package, and skill versions to `2.1.0`.
- Added README production guidance to consult the verification log before handoff.

### Verified

- Pass 1 confirmed the Israeli VAT rate as 18% from 01/01/2025 using official Israeli sources.
- Pass 2 double-confirmed the VAT rate against a 2026 tax reference and found no 2026 rate change.
- Pass 1 confirmed current API paths for Meta, TikTok, LinkedIn, data.gov.il, and Bank of Israel references.
- Pass 2 corrected LinkedIn examples because the v2 package still showed the older UGC endpoint.
- Pass 1 and Pass 2 confirmed Hebrew/RTL handling through Unicode and W3C bidirectional-text references.

## [2.0.1] - 2026-06-03

### Changed

- Moved the real client implementation to `scripts/social_media_manager_client.py` for standard Python imports.
- Added an importable CLI module and kept a small compatibility launcher.
- Updated README installation to editable install plus development requirements.
- Added a create/show quick-start chain that extracts a local identifier and reuses it.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False` and `indent=2`.
- Updated Hebrew-facing date display to `DD/MM/YYYY`.

### Fixed

- Removed decorative emoji characters from public Markdown.
- Added branding and Hebrew QA logs.
- Removed legacy hyphenated client module path.
- Confirmed package importability through `pyproject.toml`.

## [2.0.0] - 2026-06-03

### Added

- Comprehensive English `SKILL.md` with examples, edge cases, decision trees, troubleshooting, anti-patterns, and production checklist.
- Comprehensive Hebrew `SKILL_HE.md` with Israeli terminology, `₪`, `DD/MM/YYYY`, and professional local phrasing.
- API and regulation reference with platform request/response examples, Israeli compliance references, and error tables.
- End-to-end workflow guide for local services, freelancers, retail, B2B, emergency pauses, testimonials, and monthly review.
- Dedicated troubleshooting reference.
- Test scenario reference with more than 20 concrete scenarios.
- Migration checklist.
- Typed Python client with synchronous and asynchronous scheduling.
- Click-based CLI with plan, validate, export, hashtags, and next-slots commands.
- Pytest suite with more than 20 tests.
- Runnable examples.
- README, MIT license, pyproject metadata, and development requirements.

### Changed

- Renamed package to `social-media-manager`.
- Replaced the simple posting scheduler with a structured validation and scheduling helper.
- Updated metadata to version `2.0.0`.
- Expanded tags for English and Hebrew discovery.
- Changed all generated schedules to default to `pending_owner_review`.
- Added timezone-aware ISO timestamps and Hebrew display dates.

### Removed

- Branding fields.
- Author metadata.
- Distribution callouts.
- Visual decoration and external image patterns.
- Old ad-hoc scheduler interface.

### Security

- Added consent, privacy, anti-spam, consumer-offer, accessibility, and regulated-claim risk flags.
- Added explicit boundaries against scraping, fake engagement, unauthorized automation, and hidden advertising.

## [1.2.0] - Previous package

### Changed

- Earlier package included a smaller Israeli social-content guide and basic posting scheduler.
