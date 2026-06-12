# Changelog


## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation for official and terminology-sensitive claims.
- Added package constant `ISRAEL_INVOICE_ALLOCATION_THRESHOLD_ILS` for the verified 03/06/2026 contextual threshold.
- Added documentation notes for Israel Invoices threshold handling as a review note only.

### Changed

- Revalidated the 18% VAT helper value against the Israel Tax Authority and Knesset sources.
- Corrected 2026 Israel Invoices threshold context from a generic large-invoice warning to the live post-01/06/2026 threshold of above 5,000 ₪ before VAT.
- Clarified that Tax Authority API endpoint paths, API hosts, and webhook event names are not implemented by this package.
- Clarified that professional email style guidance is a product capability rather than an official regulatory claim.

### Web validation findings

- Pass 1 confirmed VAT history, Israel Invoices services, consumer complaint evidence, privacy minimization, marketing consent context, ILS usage, and business terminology.
- Pass 2 double-confirmed the same rows with different sources where available.
- One row was corrected in pass 2: Israel Invoices threshold now reflects the 01/06/2026 reduction to above 5,000 ₪ before VAT.
- One row remains not officially confirmable: professional Hebrew email greetings and signature style are not a regulated official standard.

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.1.0] - 2026-06-03

### Added

- Neutral packaging audit report at `references/branding-audit.md`.
- Hebrew quality log at `references/hebrew-qa-log.md`.
- Installable `hebrew_email_formatter` package.
- Local draft `create` and `show` workflow that returns and reuses a draft identifier.
- Public package entrypoint `hebrew-email-formatter`.
- Example scripts that read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False`.
- `pytest-asyncio` development dependency.

### Changed

- Replaced the hyphenated client script with `scripts/hebrew_email_formatter_client.py`.
- Updated imports to use the installable package.
- Updated all public documentation and examples to `DD/MM/YYYY`.
- Updated README installation instructions to include `pip install -e .`.
- Updated quick start to extract an identifier from a create response and reuse it in the next command.
- Cleaned public Markdown for emoji, visual asset links, and image references.
- Standardized Hebrew prose to neutral imperative technical voice.

### Removed

- Hyphenated client script.
- Non-installable import path workarounds.
- Cache files from the bundled package.

## [2.0.0] - 2026-06-03

### Added

- Standalone Hebrew email formatter focused on drafting rather than sending automation.
- Comprehensive English and Hebrew skill guides.
- References, workflows, troubleshooting, test scenarios, migration checklist, README, license, packaging files, client, CLI, examples, and tests.

### Removed

- Branding, visual assets, organization references, and creator metadata.
- Sending-tool assumptions from the core skill.
