# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and versioning follows semantic versioning.

## [2.2.0] - 2026-06-04

### Added
- Added `references/verification-log.md` with two-pass web validation, short source snippets, URLs, access dates, and a summary table.
- Added explicit 2026 VAT handling notes for freelancer and small-business income review.
- Added tests covering rejection of mortgage and track terms above the standard 30-year cap.

### Changed
- Corrected the standard term validation from 1-40 years to 1-30 years after validating Bank of Israel Directive 329 in pass 1 and a separate 2026 source in pass 2.
- Clarified that the package label DSR corresponds to the official payment-to-income terminology, שיעור החזר מהכנסה.
- Clarified that `existing_monthly_debt` is a conservative policy input and must be mapped carefully against the official PTI definition and lender policy.
- Updated Hebrew terminology from דירה חלופית to the official דירה חליפית.
- Updated value wording from an absolute lower-of rule to conservative lender-recognized value based on price and valuation evidence.
- Bumped project and metadata version to 2.2.0.

### Web validation findings
- Pass 1 and Pass 2 double-confirmed the standard VAT rate of 18% from 01/01/2025 as the current 2026 checked rate.
- Pass 1 and Pass 2 double-confirmed LTV caps of 75% for a single dwelling, 70% for a replacement dwelling, and 50% for an investment dwelling.
- Pass 1 and Pass 2 double-confirmed the 50% payment-to-income hard cap.
- Pass 1 and Pass 2 double-confirmed the 40% high-risk or review threshold.
- Pass 1 and Pass 2 confirmed the official payment-to-income definition and prompted documentation clarification for broader existing-debt inputs.
- Pass 1 and Pass 2 double-confirmed the 66.66% variable-rate share rule.
- Pass 1 confirmed the 30-year standard final repayment cap; Pass 2 independently confirmed it and the package was corrected.
- Pass 1 and Pass 2 double-confirmed special reduced-price apartment valuation and own-funds rules as an edge case outside the default calculation path.
- Pass 1 and Pass 2 double-confirmed the conservative need to validate property value against bank-recognized price or assessor valuation.
- Pass 1 and Pass 2 double-confirmed that approval in principle is a bank-issued document and not an output of this calculator.
- Pass 1 and Pass 2 double-confirmed the uniform mortgage basket framework used for comparison, not for local approval.
- Pass 1 and Pass 2 double-confirmed that Bank of Israel interest-rate comparison data is based on bank reports and uniform methodology rather than borrower-specific pricing.
- Pass 1 and Pass 2 double-confirmed that the credit-data register is managed by the Bank of Israel and is not queried by this package.
- Pass 1 and Pass 2 double-confirmed source-of-funds and AML review context for unexplained or gifted equity.
- Pass 1 and Pass 2 double-confirmed the need to support property-status classification with Tax Authority or lender-required documents.
- Pass 1 confirmed official Hebrew and English terminology; Pass 2 prompted Hebrew wording corrections and PTI/DSR clarification.
- Pass 1 and Pass 2 found no official public mortgage-eligibility decision webhook or endpoint applicable to this package.

## [2.1.0] - 2026-06-04

### Changed
- Moved the Python implementation to the importable `mortgage_loan_eligibility_client` module and removed the hyphenated client file.
- Added an importable CLI module with a direct wrapper script and editable-install console entry point.
- Updated quick-start commands to create a scenario, extract the returned scenario id, and evaluate it.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print JSON with `ensure_ascii=False`.
- Removed generated test cache artifacts from the bundled ZIP.

### Added
- Added branding and attribution audit report.
- Added Hebrew quality-assurance log.

## [2.0.0] - 2026-06-04

### Added

- Comprehensive English guide with examples, edge cases, mermaid decision tree, troubleshooting, anti-patterns, and production checklist.
- Hebrew guide with Israeli professional terminology, ₪ amounts, and localized examples.
- Regulation and local interface reference.
- End-to-end workflow guide.
- Dedicated troubleshooting guide.
- Test scenario reference with more than 20 scenarios.
- Migration checklist for replacing older spreadsheets or calculators.
- Typed sync and async Python client.
- Typer command-line interface.
- Pytest suite with more than 20 tests.
- Runnable example scripts.
- MIT license.
- Project configuration and development requirements.

### Changed

- Refactored package to a neutral structure.
- Expanded metadata tags.
- Standardized property statuses and result fields.
- Made DSR and rate inputs accept decimal or percent notation.

### Removed

- Attribution metadata.
- Promotional text, decorative media references, and distribution callouts.
