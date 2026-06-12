# Changelog

All notable changes to this package are documented in this file.

The format is based on Keep a Changelog, and this package follows semantic versioning.

## [2.2.0] - 2026-06-01

### Added

- Added `references/verification-log.md` with two-pass live-source validation covering VAT context, Arnona, Mas Rechush, purchase tax, betterment levy, Real Estate Taxation forms, data.gov.il CKAN API patterns, webhook status, and official terminology.
- Added live-source validation notes and public webhook policy to `references/api-reference.md`.

### Changed

- Corrected Mas Rechush 2026 vacant-land guidance to distinguish proposed 1.5% materials from an enforceable current liability.
- Bumped package metadata and Python project version to `2.2.0`.
- Expanded README index guidance to direct users to the verification log.
- Exported package `__all__` so public helper count and wildcard imports remain explicit.

### Verified

- Pass 1 confirmed current VAT context, purchase-tax bracket examples, Arnona annual-order handling, Mas Rechush direct-damage routes, Real Estate Taxation declaration forms, betterment-levy workflow, CKAN endpoint examples, and terminology.
- Pass 2 rechecked confirmed rows with alternate sources or search paths and corrected the vacant-land Mas Rechush treatment from proposal-style language to explicit caution language.

## [2.1.0] - 2026-06-01

### Added

- Added installable `property_tax_advisor` package with console entry point.
- Added local case creation and next-step chaining helpers for quick-start workflows.
- Added branding audit report and Hebrew QA log.

### Changed

- Moved real implementation from the hyphenated client filename into the installable package.
- Replaced file-path import loading with normal package imports.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print localized JSON.
- Updated Hebrew date localization to `DD/MM/YYYY`.

### Removed

- Removed the hyphenated client implementation file.

## [2.0.0] - 2026-06-01

### Added

- Expanded scope from Arnona-only guidance to Israeli property-tax triage covering Arnona, Mas Rechush, purchase tax, land appreciation tax routing, betterment levy, business sign charges, and adjacent municipal charges.
- Added comprehensive English `SKILL.md` with decision trees, examples, edge cases, anti-patterns, troubleshooting prompts, and production checklist.
- Added comprehensive Hebrew `SKILL_HE.md` with localized Israeli terminology, `₪` amounts, and `DD/MM/YYYY` date examples.
- Added `references/api-reference.md` with Israeli regulatory map, official service patterns, request/response examples, and error tables.
- Added `references/workflow-guide.md` with concrete end-to-end workflows.
- Added `references/troubleshooting.md`.
- Added `references/test-scenarios.md` with more than 20 concrete scenarios.
- Added `references/migration-checklist.md`.
- Added typed synchronous and asynchronous helper client.
- Added Click-based CLI.
- Added pytest suite with more than 20 tests.
- Added runnable examples for consumer, freelancer, small business, transaction, betterment levy, and Mas Rechush scenarios.
- Added `README.md`, `LICENSE`, `pyproject.toml`, and `requirements-dev.txt`.

### Changed

- Renamed package slug to `property-tax-advisor`.
- Bumped version to `2.0.0`.
- Expanded metadata tags for consumers, freelancers, and small businesses.

### Removed

- Removed creator metadata.
- Removed visual identity references and distribution callouts.
