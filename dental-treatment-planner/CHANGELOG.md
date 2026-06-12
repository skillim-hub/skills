# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [0.4.0] - 2026-06-04

### Added
- `references/verification-log.md` with a mandatory two-pass live-source validation table and summary counts.
- Web-validated source snapshots in the English and Hebrew guides.
- API-reference wording that states local `/v1/...` examples are implementation contracts, not official provider endpoints.
- Explicit webhook section stating no public provider webhook event names are confirmed for this package.

### Changed
- Updated the default VAT simulation rate to 18% after live validation against Tax Authority, Knesset and 2026 tax-summary sources.
- Clarified that provider factors are heuristic planning coefficients, not official discounts or binding tariffs.
- Expanded child and senior eligibility wording using Ministry of Health terminology.
- Refined Hebrew terminology for `שירותי בריאות השן`, `טיפולי שיניים מונעים`, `טיפולים משמרים`, `השתתפות עצמית`, and `תוכנית טיפול`.
- Bumped package metadata and Python project version to 0.4.0.

### Verified
- Pass 1 confirmed the VAT increase to 18% from 01/01/2025 through Tax Authority material.
- Pass 2 confirmed the 2026 VAT rate through a different tax-summary source reviewed on 01/01/2026.
- Pass 1 and Pass 2 confirmed Ministry of Health child dental eligibility from birth to age 18.
- Pass 1 and Pass 2 confirmed age 72 and above dental-benefit terminology through Ministry of Health and HMO sources.
- Pass 1 and Pass 2 confirmed Maccabident source handling through the official 2026 tariff PDF and rights page.
- Pass 1 and Pass 2 confirmed Clalit Smile and Clalit Mushlam plan-specific examples through current Clalit pages.
- Pass 1 and Pass 2 confirmed private dental prices are highly variable and must remain planning ranges.
- Pass 1 and Pass 2 did not confirm a public provider tariff API or public webhook events; the package now states local-only interface assumptions.

### Fixed
- Corrected stale 17% VAT default in the client, context parsing and tests.
- Updated warnings to say VAT at 18% is added only when `include_vat=true`.
- Removed stale or ambiguous wording that could imply HMO provider factors are official percentages.

## [0.3.0] - 2026-06-04

### Added
- Installable `dental_treatment_planner` package with direct imports after `pip install -e .`.
- `create` CLI workflow that returns a `plan_id` for chained estimate commands.
- `references/branding-audit.md` with grep results and remediation notes.
- `references/hebrew-qa-log.md` with Hebrew localization and terminology review notes.
- Environment-aware runnable examples that accept `--env sandbox|production` and read `DTP_*` variables.

### Changed
- Replaced hyphenated client implementation with underscored client helper and package imports.
- Standardized local-facing dates to DD/MM/YYYY while preserving ISO and legacy dash parsing.
- Updated README installation commands to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Added `pytest-asyncio` to development requirements.
- Removed cache artifacts from the distributable archive.

### Fixed
- Removed path-based import loading from CLI and tests.
- Updated metadata entrypoints to use underscored client helper paths.
- Confirmed public Markdown contains no emoji, external status images or visual-brand references.

## [0.2.0] - 2026-06-04

### Added
- English and Hebrew guides with Israeli dental-planning workflows.
- Offline reference contracts, workflow guide, troubleshooting guide, test scenarios, migration checklist, README, MIT license, pyproject, and development requirements.
- Typed Python estimator client with sync and async estimate methods.
- Typer CLI with sample, template, validate, estimate, compare, schedule, and catalog commands.
- Pytest coverage for catalog, date parsing, validation, coverage, provider comparison, async estimate, schedule generation, serialization, and CSV export.

### Changed
- Removed branding, author metadata, visual branding and distribution callouts.

## [0.1.0] - 2026-06-04

### Added
- Initial package skeleton.
