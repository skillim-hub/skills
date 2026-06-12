# Changelog

All notable changes to this package are documented in this file.

The format is based on Keep a Changelog, and this project follows semantic versioning.


## [2.1.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, status tags, and summary counts.
- Added official-source references for Tax Authority VAT history, VAT rates, dealer registration services, Israel Invoice allocation-number services, and Knesset law pages.
- Added a high-value B2B allocation-number workflow and troubleshooting entry.

### Changed

- Bumped metadata and package version to 2.1.0.
- Clarified that 18% VAT is the validated 2026 standard example rate, while keeping `vat_rate` configurable.
- Updated Hebrew guidance with מספר הקצאה, תקרה לפני מע״מ, ניכוי מע״מ תשומות, and localized 2026 threshold dates.
- Replaced broad or non-official legal-source references with specific official service and legislation links.

### Fixed

- Corrected the v2 broad business-registration URL into specific official Tax Authority service references.
- Removed the non-official legal repository reference from the official-source list.
- Logged and rejected a stale third-party 2026 VAT article that still stated 17%.

## [2.0.0] - 2026-06-02

### Added

- Installable `free_text_invoice_explanation` Python package.
- Typed synchronous and asynchronous client methods.
- Typer-based CLI with `explain` and `one` commands.
- Runnable examples that read environment variables and accept `--env sandbox|production`.
- Branding audit report.
- Hebrew quality assurance log.
- Expanded troubleshooting, workflow, test scenario, and migration references.

### Changed

- Moved importable implementation to an underscored Python module path.
- Updated README install instructions to use `pip install -e .` and development requirements.
- Updated quick-start workflow to extract an explanation identifier from the create response and reuse it.
- Improved Hebrew terminology, date localization, and VAT phrasing.
- Removed public Markdown emoji, visual-asset references, and branding references.

### Fixed

- Removed the non-importable hyphenated client module.
- Added `pytest-asyncio` to development requirements.
- Ensured examples use `json.dumps(..., ensure_ascii=False, indent=2)`.
- Ensured tests and script syntax checks pass.

## [1.0.0] - 2026-06-02

### Added

- Initial enhanced package with bilingual skill guidance, references, scripts, examples, tests, and metadata.
