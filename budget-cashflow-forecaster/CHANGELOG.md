# Changelog

All notable changes to this package are documented in this file. The format follows Keep a Changelog, and the package uses semantic versioning.



## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, and confirmation status.
- Added validated 2026 VAT, income-tax advance, Bituach Leumi, withholding-tax, and Bank of Israel exchange-rate reference notes.

### Changed

- Corrected Bank of Israel exchange-rate integration guidance to prefer the current `edge.boi.gov.il/FusionEdgeServer/...` series API.
- Reclassified `boi.org.il/PublicApi/GetExchangeRates` as a legacy/simple endpoint rather than the preferred integration path.
- Updated business examples to use `bituach_leumi_rate: 0.18` as a conservative flat planning approximation, reflecting the 2026 regular combined self-employed bracket.
- Clarified that Bituach Leumi is bracketed and should be calculated from exact vouchers or official brackets for production planning.
- Clarified VAT and income-tax advance timing distinction between statutory 15th-of-month planning and online 19th-of-month filing/payment where applicable.

### Verified

- VAT rate: 18%, effective 01/01/2025 and still used in 2026 references.
- VAT online reports: online filing/payment may be made by the 19th when applicable.
- Income-tax advances: online service handles periodic advance reporting/payment.
- Bituach Leumi 2026 self-employed brackets: ₪7,703 reduced bracket, ₪51,910 maximum base, 7.7%/18% combined rates.
- Withholding-tax lookup: information service rather than a filing API.
- Webhook events: not applicable for this local non-API skill.

## [2.1.0] - 2026-06-02

### Added

- Added branding and visual-reference audit report.
- Added Hebrew quality-assurance log.
- Added installable `budget_cashflow_forecaster` Python package.
- Added saved forecast `create` and `show` CLI flow with forecast ids.
- Added `sandbox` and `production` environment mode to CLI and examples.

### Changed

- Moved implementation from a hyphenated script into an underscored installable module.
- Updated README installation to use editable package installation.
- Updated examples to read environment variables, accept `--env`, and print JSON with `ensure_ascii=False`.
- Updated Hebrew date localization to `DD/MM/YYYY`.

### Removed

- Removed hyphenated client implementation script.
- Removed generated cache artifacts from the packaged archive.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide with examples, edge cases, Mermaid decision tree, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew guide with Israeli terminology, ₪ formatting guidance, and `DD/MM/YYYY` display guidance.
- Israeli regulation and data reference with official-source mapping, request/response examples, and error tables.
- Workflow guide for freelancers, עוסק מורשה, עוסק פטור, retailers, households, migration, monthly close, stress testing, review pack, and recovery planning.
- Troubleshooting reference.
- Test scenario reference with more than 20 concrete scenarios.
- Migration checklist.
- Typed sync and async Python helper.
- Click-based CLI.
- Pytest suite with more than 20 tests.
- Runnable examples.
- Project README.
- MIT license.
- `pyproject.toml` and `requirements-dev.txt`.

### Changed

- Rebuilt package structure for local-first use.
- Bumped metadata version to `2.0.0`.
- Expanded metadata tags.
- Converted tax values to configurable planning inputs.

### Removed

- Promotional wording.
- Visual marks and image references.
- Creator metadata.
- First-person voice.

### Security

- Added guidance to avoid sharing live customer, bank, or tax data publicly.
