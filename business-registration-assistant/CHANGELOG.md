# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows semantic versioning for package documentation.

## [2.2.0] - 2026-06-02

### Added

- Web-validated `references/verification-log.md` with Pass 1 and Pass 2 source matrix.
- Live-verified 2026 values for VAT, עוסק פטור ceiling, Bituach Leumi tests, Form 821, Form 6101, and cash-use checks.
- Additional tests for the verified 2026 עוסק פטור ceiling boundary.

### Changed

- Bumped metadata and package version to 2.2.0.
- Updated README and examples to use the verified 2026 ceiling value of ₪122,833.
- Added combined online opening route notes for Tax Authority and Bituach Leumi workflows.

### Fixed

- Corrected 2026 planning examples that still used ₪120,000 where the current 2026 ceiling is ₪122,833.
- Corrected System 1000 supplier wording to the current 3,000-supplier source.

### Web validation findings

- Pass 1 confirmed the standard Israeli VAT rate as 18% from the Tax Authority VAT history.
- Pass 2 confirmed the VAT rate against an independent international tax summary.
- Pass 1 confirmed the VAT rate increase from 17% to 18% in the Tax Authority interpretation material.
- Pass 2 confirmed the 01/01/2025 effective date through the Knesset publication.
- Pass 1 confirmed the 2026 עוסק פטור ceiling as ₪122,833 through the Tax Authority service page.
- Pass 2 confirmed the same ₪122,833 ceiling through Kol Zchut and the small-business reform material.
- Corrected prior planning examples from ₪120,000 to ₪122,833 where a 2026 ceiling value was intended.
- Pass 1 confirmed the Regulation 13 occupation restriction from the Tax Authority service page.
- Pass 2 confirmed the occupation restriction through Kol Zchut.
- Pass 1 confirmed that online עוסק פטור opening covers VAT and income tax.
- Pass 2 confirmed the Tax Authority VAT topic page links the same online service.
- Pass 1 confirmed a combined Tax Authority and Bituach Leumi opening route from a government announcement.
- Pass 2 confirmed the combined route through a separate procedural source.
- Pass 1 confirmed Form 821 for authorized dealer opening.
- Pass 2 confirmed Form 821 and supporting documents through a separate procedural source.
- Pass 1 confirmed bank confirmation or cancelled check requirements.
- Pass 2 confirmed bank-account evidence as a registration document.
- Pass 1 confirmed Bituach Leumi self-employed tests for 2026: 20 hours, ₪6,885, and ₪2,065 with 12 hours.
- Pass 2 confirmed the Bituach Leumi tests through a separate procedural source.
- Pass 1 confirmed Form 6101 as the Bituach Leumi opening or change form.
- Pass 2 confirmed the same function through the government annual-report service.
- Pass 1 confirmed the ₪51,910 Bituach Leumi income cap for employee plus self-employed status.
- Pass 2 confirmed the same cap through a separate Bituach Leumi status page.
- Pass 1 confirmed adult self-employed Bituach Leumi contribution components and totals.
- Pass 2 confirmed the same rates through a Bituach Leumi calculation example.
- Pass 1 confirmed that עוסק פטור cannot issue VAT tax invoices.
- Pass 2 confirmed receipt-only handling through a separate VAT-file procedural page.
- Pass 1 confirmed the annual exempt dealer turnover declaration service.
- Pass 2 confirmed the once-per-year declaration concept through a separate source.
- Pass 1 confirmed online VAT report and payment service availability.
- Pass 2 confirmed reporting distinctions through a procedural VAT source.
- Pass 1 confirmed withholding and bookkeeping certificate information.
- Pass 2 corrected System 1000 supplier coverage to the current 3,000-supplier wording.
- Pass 1 confirmed VAT dealer lookup by dealer number.
- Pass 2 confirmed displayed lookup fields.
- Pass 1 confirmed cash-use restrictions for transactions with dealers above ₪6,000.
- Pass 2 confirmed the Tax Authority cash-use simulator.
- Pass 1 confirmed that no official government API submission is implemented in the package.
- Pass 2 confirmed the package uses a local JSON case workflow and no official webhooks.

## [2.1.0] - 2026-06-02

### Added

- Branding, author, logo, and emoji audit report.
- Hebrew quality assurance change log.
- Installable `business_registration_assistant` Python package.
- Case creation and case-plan workflow for chained quick-start usage.
- Package console script entry point.
- Environment-aware runnable examples with `--env sandbox|production`.

### Changed

- Replaced the hyphenated client script with an underscored client script.
- Updated CLI and examples to import the installable package without path hacks.
- Updated README installation to use `pip install -e .` and development requirements.
- Localized Hebrew dates to DD/MM/YYYY format.
- Bumped metadata version to 2.1.0.

### Fixed

- Removed generated cache artifacts from the final bundle.
- Confirmed pytest and compileall execution in the final verification pass.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English and Hebrew guides.
- Regulatory/API-style reference.
- Workflow guide and document-workflow alias.
- Troubleshooting reference.
- Migration checklist.
- Test scenarios with more than 20 cases.
- Typed sync/async Python client.
- Typer CLI.
- Runnable examples.
- Pytest suite with more than 20 tests.
- MIT license.
- Python development configuration.

### Changed

- Removed branding, visual promotional references, and author metadata.
- Expanded metadata tags.
- Converted wording to neutral imperative guidance.
- Clarified that עוסק פטור is not exempt from income tax or Bituach Leumi.
