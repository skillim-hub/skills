# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.

## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation for Israeli VAT, disclosure, privacy, spam, accessibility, invoice-allocation, and regulated-category references.
- Added planning constants for the standard Israeli VAT rate and effective date, validated as of 03/06/2026.
- Added source notes for official-service applicability, API hosts, endpoint paths, and webhook event names.

### Changed

- Standardized Hebrew VAT terminology to `מע"מ`.
- Clarified that commercial disclosure must be clear and Hebrew-facing, without claiming one exact phrase is the only possible wording.
- Updated the API and regulation reference to distinguish official services from offline local helper behavior.
- Updated README file index and operational notes to include the verification log.

### Verified

- Double-confirmed the 18% VAT rate effective 01/01/2025 and still reflected in 2026 official materials.
- Double-confirmed consumer-protection treatment of misleading commercial content and online influencer or blogger reviews.
- Double-confirmed spam, direct-mailing, privacy, accessibility, lottery, alcohol, financial-advice, and health-claim escalation points.
- Confirmed no official Israeli influencer registry API, API host, endpoint path, or webhook event name is used by this offline package.

## [2.1.0] - 2026-06-03

### Added

- Added branding and public Markdown audit report.
- Added Hebrew quality assurance log.
- Added importable underscored client module at `scripts/influencer_collaboration_client.py`.
- Added importable Typer CLI module at `scripts/influencer_collaboration_cli.py`.
- Added local brief creation and brief identifier workflow for chained quick-start commands.
- Added editable installation configuration through `pyproject.toml`.
- Added async test coverage and compile validation support.
- Added environment-aware runnable examples with Hebrew-safe JSON output.

### Changed

- Removed the hyphenated client implementation path.
- Updated README installation to use editable installation and development requirements.
- Updated examples to accept `--env sandbox|production`.
- Updated Hebrew documentation for neutral imperative voice, local date format, and ₪ notation.
- Expanded regulation and integration reference tables.
- Expanded troubleshooting and migration guidance.

### Fixed

- Fixed import paths to avoid path manipulation.
- Fixed quick-start flow so the identifier from a create response is reused in the next command.
- Fixed public Markdown to avoid external status images, visual-identity references, and decorative symbols.
- Fixed development requirements to include async test support.

## [2.0.0] - 2026-06-03

### Added

- Added English and Hebrew skill guides.
- Added local client, CLI, tests, examples, and references.
- Added workflow, troubleshooting, test scenario, and migration documents.
- Added MIT license and package metadata.
