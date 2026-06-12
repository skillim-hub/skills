# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.1.0] - 2026-06-04

### Added

- Added `references/verification-log.md` with two-pass web validation for all Israeli official/regulatory/API sources referenced by the package.
- Added verified 2026 source highlights to `metadata.json`.
- Added verified official API patterns for Bank of Israel interest and exchange-rate data.
- Added verified CBS CPI endpoint patterns.
- Added the verified 2026 osek patur threshold of ₪122,833 as a dated reference note.
- Added dated source notes for VAT, National Insurance, arnona, electricity, water, public transport, health, banking fees, minimum wage, and Capital Market Authority references.

### Changed

- Bumped package version to 2.1.0.
- Replaced the illustrative VAT-rate pseudo-endpoint with a manual verified-rate record based on Tax Authority sources.
- Replaced the illustrative CPI pseudo-endpoint with actual CBS public API endpoint patterns.
- Clarified that 18% VAT remains configurable and is verified for examples from 01-01-2025 onward.
- Clarified that National Insurance figures are context for reserve planning only and not final liability calculation.
- Updated English and Hebrew guides to include annual verification of the osek patur threshold.
- Updated README with the web-validated source note.

### Web validation findings

- Pass 1 and Pass 2 confirmed the current Israeli VAT example rate.
- Pass 1 and Pass 2 confirmed the official VAT rates/amounts source.
- Pass 1 and Pass 2 confirmed the 2026 osek patur threshold.
- Pass 1 found the VAT pseudo-endpoint could not be confirmed; Pass 2 corrected it to manual official-rate verification.
- Pass 1 and Pass 2 confirmed income-tax payment and advance-payment source language.
- Pass 1 and Pass 2 confirmed VAT and income-tax reporting source language for 2026.
- Pass 1 and Pass 2 confirmed 2026 National Insurance self-employed rate-band context.
- Pass 1 and Pass 2 confirmed National Insurance self-employed status context.
- Pass 1 and Pass 2 confirmed the Bank of Israel interest API host/path.
- Pass 1 and Pass 2 confirmed the Bank of Israel exchange-rate API host/path.
- Pass 1 found the CPI pseudo-endpoint could not be confirmed; Pass 2 corrected it to CBS public API endpoints.
- Pass 1 and Pass 2 confirmed CBS price-index and CPI source language.
- Pass 1 and Pass 2 confirmed Israeli household expenditure source language.
- Pass 1 and Pass 2 confirmed 2026 electricity tariff source language.
- Pass 1 and Pass 2 confirmed Electricity Authority regulator source language.
- Pass 1 and Pass 2 confirmed 2026 Water Authority tariff source language.
- Pass 1 and Pass 2 confirmed Water Authority source language.
- Pass 1 and Pass 2 confirmed arnona calculation and municipal tariff source language.
- Pass 1 and Pass 2 confirmed local discretion for arnona discounts.
- Pass 1 and Pass 2 confirmed Rav-Kav terminology and public-transport authority source language.
- Pass 1 and Pass 2 confirmed public-transport fare and concession source language.
- Pass 1 and Pass 2 confirmed Kupat Cholim and HMO terminology.
- Pass 1 and Pass 2 confirmed SHABAN supplementary insurance terminology.
- Pass 1 and Pass 2 confirmed Bank of Israel banking-fee schedule guidance.
- Pass 1 and Pass 2 confirmed minimum-wage source language.
- Pass 1 and Pass 2 confirmed Capital Market Authority pension/provident-fund source language.
- Pass 1 and Pass 2 confirmed that webhook event names are not applicable because the package has no webhook workflow.

## [2.0.1] - 2026-06-04

### Added

- Branding and visual-reference audit report.
- Hebrew quality-assurance log.
- Installable Python package with `household_budget_planner` imports.
- Chained CLI create flow returning a budget identifier.
- Syntax verification through `compileall`.

### Changed

- Replaced hyphenated Python implementation files with underscored importable modules.
- Updated README installation to editable package installation plus development requirements.
- Updated examples to accept environment selection and print JSON with Unicode preserved.
- Localized Hebrew technical prose to ₪ and `DD/MM/YYYY`.

### Removed

- Legacy hyphenated client and CLI implementation files.

## [2.0.0] - 2026-06-04

### Added

- Comprehensive English guide with Israeli examples, edge cases, Mermaid decision trees, troubleshooting, anti-patterns, and production checklist.
- Comprehensive Hebrew guide with Israeli professional terminology, ₪ amounts, and `DD-MM-YYYY` dates.
- Israeli API/regulation/reference guide with source table, request/response examples, and error table.
- Workflow guide for household budgeting, freelancer cash-flow split, credit-card audits, emergency funds, annual sinking funds, shared households, and monthly review.
- Dedicated troubleshooting guide.
- Test-scenario guide with 30 scenarios.
- Migration checklist.
- Typed synchronous and asynchronous Python client.
- Typer CLI.
- Pytest suite with more than 20 tests.
- Six runnable example scripts.
- README, MIT license, pyproject, and development requirements.

### Changed

- Renamed skill slug to `household-budget-planner`.
- Expanded tags for Israeli household, freelancer, small-business, and consumer budgeting.
- Converted rate guidance to verification-first references instead of hard-coded advice.

### Removed

- Branding, visual identity assets, creator metadata, and distribution callouts.
