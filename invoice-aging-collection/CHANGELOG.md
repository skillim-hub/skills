# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and versioning follows Semantic Versioning.

## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with mandatory two-pass web validation, source URLs, access date, and short quoted snippets.
- Added verified 2026 figures for VAT, small-claims ceiling and fee, fixed-amount enforcement ceiling, enforcement fees, Israel Invoice thresholds, WhatsApp integration fields, and email authentication.
- Added Israel Invoice API endpoint examples for accounting integrations while preserving the reminder-only boundary.

### Changed

- Updated WhatsApp documentation from a hardcoded Graph API version to `{GRAPH_API_VERSION}`.
- Updated both English and Hebrew guides with tax and filing boundary rules.
- Bumped package metadata and project version to 2.2.0.

### Fixed

- Corrected a Hebrew typo in the interest verification instruction.
- Kept statutory interest, VAT, court filing, and enforcement-cost handling conditional on live verification and human review.

### Web-validation findings

- VAT: Pass 1 confirmed 18% from Tax Authority VAT history; Pass 2 confirmed 18% in a 2026 official accounting exam.
- Small-claims ceiling: Pass 1 confirmed ₪39,900 on the Judicial Authority filing service; Pass 2 confirmed the same figure through an independent public legal-rights reference.
- Small-claims fee: Pass 1 confirmed 1% with ₪50 minimum; Pass 2 confirmed the 1% fee rule on the courts fee reference.
- Fixed-amount enforcement: Pass 1 confirmed a ₪75,000 ceiling; Pass 2 confirmed the same threshold through Enforcement Authority forms guidance.
- Enforcement fees: Pass 1 confirmed 2026 regular and short-route fee formulas; Pass 2 confirmed the current 2026 fee-table publication page.
- Interest/linkage: Pass 1 confirmed the 01/01/2025 reform start; Pass 2 confirmed that installment arrangements can affect arrears fees.
- Payment Ethics Law: Pass 1 confirmed the law regulates supplier payment timing; Pass 2 confirmed maximum supplier payment timing language.
- Privacy: Pass 1 confirmed digital personal-data protection responsibility; Pass 2 confirmed privacy risk reduction for collected personal data.
- Communications Law 30A: Pass 1 confirmed the advertising-message definition; Pass 2 confirmed consent guidance for electronic messages.
- Consumer protection: Pass 1 confirmed truthful consumer information terminology; Pass 2 confirmed consumer personal/household-use terminology.
- Israel Invoice thresholds: Pass 1 confirmed ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026; Pass 2 confirmed the ₪5,000 framing in Tax Authority professional guidance.
- Israel Invoice API: Pass 1 confirmed the approval endpoint; Pass 2 confirmed the invoice-information endpoint family.
- WhatsApp messages API: Pass 1 confirmed the Messages API; Pass 2 confirmed Cloud API messaging terminology.
- WhatsApp Hebrew templates: Pass 1 confirmed `he`; Pass 2 confirmed one-language-per-template practice.
- WhatsApp webhooks: Pass 1 confirmed webhook JSON payloads; Pass 2 confirmed Meta Graph API real-time webhook notification terminology.
- Email authentication: Pass 1 confirmed Google sender authentication requirements; Pass 2 confirmed DMARC's RFC definition.

## [2.1.0] - 2026-06-02

### Changed

- Replaced the hyphenated client file with an underscored importable client module.
- Added an installable project configuration for editable installs and console entry points.
- Updated Hebrew-facing dates and examples to DD/MM/YYYY while keeping legacy import parsing.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False`.
- Updated README installation and quick-start commands to chain the created invoice ID into a follow-up command.
- Added branding audit and Hebrew quality log references.

### Fixed

- Removed dynamic import loaders from the CLI, tests, and examples.
- Confirmed public Markdown contains no visual marketing references or emoji.
- Kept the MIT license notice neutral.


## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with decision trees, edge cases, troubleshooting, anti-patterns, and production checklist.
- Full Hebrew guide with Israeli professional terminology, ₪ currency formatting, and DD/MM/YYYY date localization.
- Regulation and integration reference covering Israeli collection-related laws, government service links, JSON/CSV, WhatsApp, email, and registered mail workflows.
- End-to-end workflow guide.
- Dedicated troubleshooting guide.
- Test scenarios reference with 30 concrete scenarios.
- Migration checklist for spreadsheets and older workflows.
- Typed Python client/helper with synchronous and asynchronous APIs.
- Typer CLI for sample data, validation, aging reports, reminder generation, rendering, CSV import, evidence export, and dispatch dry-runs.
- Pytest suite with more than 20 passing tests.
- Five runnable examples.
- Project configuration and development requirements.
- MIT license using neutral copyright attribution.

### Changed

- Renamed the skill to `invoice-aging-collection`.
- Reworked metadata for neutral tags and descriptions.
- Removed non-neutral package metadata.
- Removed non-neutral package references.
- Reframed collection language around human review and factual, respectful Hebrew.

### Removed

- Branding references.
- Non-neutral metadata fields.
- Visual promotional references.
- Non-operational promotional callouts.
