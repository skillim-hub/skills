# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [1.2.0] - 2026-06-02

### Added

- Web-validated official source register in `references/api-reference.md`.
- Two-pass verification log in `references/verification-log.md` with Pass 1 and Pass 2 sources, quoted snippets, access dates, and action notes.
- Tests for official Bank of Israel identification-code corrections for code `9` and code `54`.

### Changed

- Clarified that `₪50,000` production approval and `₪1,000,000` high-value routing are internal configurable controls, not official limits.
- Updated value-date guidance to distinguish Friday or holiday-eve short business days from Saturday or holiday closures.
- Updated API reference to document regulated open-banking payment-initiation endpoint patterns separately from manual bank-form preparation.
- Added official notification terminology for open-banking adapters: `SCA`, `PROCESS`, `LAST`, `revokedByPsu`, and related consent-status values.
- Documented that VAT at 18% is relevant only to tax-payment purpose or accounting context and does not validate bank transfer data.

### Fixed

- Corrected Bank of Israel identification-code mapping: code `9` is D.I. Postal Finance Ltd, and code `54` is Bank of Jerusalem Ltd.
- Replaced the stale `value_date_weekend` warning path with `value_date_calendar_check` for Friday and Saturday calendar-risk handling.
- Removed the implication that the helper phrase is official terminology; it remains a package name and neutral description only.

## [1.1.0] - 2026-06-02

### Added

- Branding and provenance audit report.
- Hebrew quality-assurance log.
- Importable underscored client module for normal Python imports.
- Importable CLI module plus direct script wrapper.
- Local record creation, lookup, listing, and payload chaining.
- Production approval warning for high-value transfers without an approver.
- Environment-aware examples with `--env sandbox|production`.
- Expanded pytest coverage for validation, async helpers, CLI, and local record chaining.

### Changed

- Removed hyphenated client module and updated imports to `domestic_bank_transfer_helper_client`.
- Updated installation instructions to `pip install -e .` followed by `pip install -r requirements-dev.txt`.
- Updated quick start to extract an identifier from a create response and reuse it in the payload step.
- Updated Hebrew localization to use professional Israeli terminology, ₪ amounts, and `DD/MM/YYYY` operator-facing dates.
- Updated packaging so installed users can import the client without path changes.

### Fixed

- Removed generated cache files from the bundle.
- Removed public Markdown emoji, visual asset and provenance risks.
- Added `pytest-asyncio` to development requirements.

## [1.0.0] - 2026-06-02

### Added

- Complete English skill guide with MASAV/Zahav decision tree, examples, edge cases, troubleshooting, anti-patterns, and production checklist.
- Complete Hebrew skill guide with Israeli professional terminology, ₪ examples, and localized date guidance.
- API and regulation reference for internal validation payloads and non-API workflow equivalents.
- End-to-end workflow guide.
- Troubleshooting reference.
- Test scenarios reference with more than 20 cases.
- Migration checklist.
- Typed Python validation client.
- Click CLI.
- Pytest suite with more than 20 tests.
- Runnable scenario examples.
- README, MIT license, packaging metadata, and development requirements.
