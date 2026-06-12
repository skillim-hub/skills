# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog conventions, and version numbers use semantic versioning.

## [1.2.0] - 2026-06-02

### Added
- Added `references/verification-log.md` with pass 1 and pass 2 web validation sources, snippets, URLs, and access dates.
- Added VAT helpers: `gross_from_net` and `vat_components_from_gross`.
- Added statutory cancellation fee cap helper for the lower of 5% or ₪100 after eligibility review.
- Added CLI commands `vat` and `cancellation-fee-cap`.
- Added tests for current VAT baseline, VAT splitting, cancellation cap helpers, and new CLI commands.

### Changed
- Bumped the reviewed Israeli VAT baseline to 18% from 01/01/2025 based on two-source validation.
- Clarified that Bank of Israel 3.75% is a benchmark on the access date, not a customer-rate default.
- Corrected Israel Invoice 2026 threshold guidance after second-pass validation: over ₪10,000 before VAT from 01/01/2026 and over ₪5,000 before VAT from 01/06/2026.
- Strengthened consumer price-display, VAT-inclusive, cancellation, credit-disclosure, and invoice-threshold language across English and Hebrew docs.
- Added migration notes for stale Israel Invoice API descriptions.

### Verified
- Pass 1 confirmed VAT rate, price-display duties, cancellation timing, cancellation-fee cap, credit-disclosure terminology, current Bank of Israel benchmark, and invoice-threshold sources.
- Pass 2 double-confirmed the same items using different sources where available.
- Pass 2 corrected stale Israel Invoice threshold information found in an older API model document.

## [1.1.0] - 2026-06-02

### Added
- Added branding audit report and Hebrew QA log.
- Added installable Python package under `installment_calculator`.
- Added public CLI entry point through `pyproject.toml`.
- Added slash-date localization support for `DD/MM/YYYY`.
- Added environment-aware examples that read environment variables and print JSON with `ensure_ascii=False`.

### Changed
- Moved client import surface to an underscored script path and removed the hyphenated client module.
- Updated README installation to use `pip install -e .` plus development requirements.
- Updated quick start to keep a created plan and reuse it in the next operation.
- Standardized Hebrew documentation to professional Israeli terminology and neutral imperative voice.
- Expanded tests for package imports, CLI JSON, async behavior, errors, date parsing, and refund estimates.

### Removed
- Removed generated cache folders and bytecode artifacts from the bundle.
- Removed public Markdown emoji, external visual-link references, personal attribution metadata, and branding callouts.

## [1.0.0] - 2026-06-02

### Added
- Full English and Hebrew operating guides.
- Regulation and local API reference for Israeli installment disclosure work.
- Workflow guide for checkout, quotes, invoices, refunds, and plan comparison.
- Troubleshooting guide for rounding, effective cost, VAT, dates, fees, and cancellation cases.
- Test-scenario catalog with more than 20 concrete cases.
- Migration checklist for replacing spreadsheets or checkout logic.
- Typed Python calculation helper with sync and async interfaces.
- Click-based CLI for tables, JSON output, comparison, and refund estimates.
- Runnable example scripts for common Israeli use cases.
- Pytest suite with more than 20 passing tests.

### Removed
- Removed branding, external visual-link references, personal attribution fields, and distribution callouts.
