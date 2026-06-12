# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and the package uses semantic versioning.


## [2.2.0] - 2026-06-03

### Added

- Web verification log with two-pass validation for Israeli Patent Office services, official search fields, 2026 fee sources, PCT references, Nice Classification, Madrid Protocol, Paris Convention, core Israeli IP statutes, and VAT status.
- Live-source validation notes in English and Hebrew guides.
- API-reference section recording the 03/06/2026 operational validation findings.

### Changed

- Clarified that the helper does not hardcode ordinary filing fees and that current fees must be checked against the live Israel Patent Office fee table.
- Updated Nice Classification guidance to reference NCL(13-2026), effective 01/01/2026.
- Updated Madrid Protocol reference wording to the regulations in force on 01/11/2025.
- Confirmed the package does not rely on public JSON API hosts, endpoint paths, or webhook event names.

### Verified

- Pass 1 and Pass 2 double-confirmed the Israel Patent Office authority description, trademark registration service, patent registration service, official trademark search fields, 2026 fee-source existence, PCT fee-source currency, Paris Convention scope, Israeli trademark/patent/design legal references, and VAT status.
- Pass 2 corrected or sharpened two rows: the current Nice Classification version and Madrid Protocol regulations version.

## [2.1.0] - 2026-06-03

### Added

- Branding and attribution audit report.
- Hebrew quality-assurance log.
- Installable Python package with public imports from `trademark_patent_helper`.
- CLI `create` and `show` commands for local request-ID chaining.
- Environment selection for CLI and examples using `--env sandbox|production`.

### Changed

- Replaced the hyphenated client implementation with an underscore compatibility module and installable package implementation.
- Updated README installation to use editable package installation.
- Updated README quick start to extract a request ID from `create` output and reuse it with `show`.
- Updated examples to read environment variables and emit JSON with `ensure_ascii=False` and indentation.
- Standardized Hebrew-localized dates to `DD/MM/YYYY`.
- Expanded tests for package imports, local create/show flow, and environment handling.

### Removed

- Hyphenated client implementation file.
- Remaining creator-credit wording and non-neutral phrasing found during audit.


## [2.0.0] - 2026-06-03

### Added

- Comprehensive English guide with examples, edge cases, decision trees, troubleshooting, anti-patterns, and production checklist.
- Comprehensive Hebrew guide with Israeli terminology, ₪ examples, and DD/MM/YYYY localization.
- Official-source and structured helper reference for Israeli trademark and patent workflows.
- End-to-end workflow guide.
- Document workflow templates.
- Troubleshooting guide.
- Test scenario reference with 30 scenarios.
- Migration checklist.
- Typed local Python helper client with synchronous and asynchronous assessment methods.
- Click-based CLI with `assess`, `intake`, `batch`, and `template` commands.
- Pytest suite with more than 20 tests.
- Runnable examples.
- MIT license file.
- Python project configuration and development requirements.

### Changed

- Expanded from patent-only guidance to trademark and patent filing preparation.
- Refactored tone to neutral imperative guidance.
- Expanded metadata tags and raised package version.
- Structured non-API workflow around official Israeli Patent Office processes and legal sources.

### Removed

- Branding, badges, banners, package image references, attribution metadata, and distribution callouts.
- Author field from metadata.
