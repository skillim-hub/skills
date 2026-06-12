# Changelog

All notable changes to this package are documented in this file.

## [1.2.0] - 2026-06-04

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, short source snippets, access date, and summary counts.
- Added 2026 web-validated baseline notes to the English and Hebrew skill guides.
- Added tests for the six-day annual-leave entitlement transition from 23 days in the 12th seniority year to 24 days from the 13th year onward.
- Added migration and troubleshooting notes for v1 and v2 installations that used the previous six-day year-12 value.

### Changed

- Updated the regulatory reference to distinguish statutory annual-leave floors from more generous short-workweek extension-order arrangements.
- Updated terminology from generic parental leave wording to official birth and parenthood leave terminology in public documentation.
- Clarified that VAT is verified as 18% from 01/01/2025 but is reference-only and not part of leave-balance calculations.
- Clarified that no official leave-balance API endpoint paths or webhook event names are exposed by the reviewed Israeli sources; the package remains a local CLI and Python client.

### Fixed

- Corrected the six-day workweek statutory net annual-leave entitlement for the 12th seniority year from 24 to 23 days; the 24-day cap starts from the 13th year.
- Updated client constants, automated tests, examples guidance, English guide, Hebrew guide, API/reference guide, troubleshooting, migration notes, and test scenarios to match the corrected table.
- Added a 2026 reserve-duty extension-order review warning instead of encoding a universal automatic rule.

### Web validation findings

- VAT: double-confirmed at 18% from 01/01/2025.
- Annual leave: double-confirmed statutory table, 5-day extension-order caveat, gross-to-net conversion, and excluded absence categories.
- Sick leave: double-confirmed accrual of 1.5 days per full month, 90-day cap, and statutory sick-pay percentages.
- Miluim: double-confirmed employer wage-payment and Form 501 reimbursement workflow.
- Birth and parenthood leave: double-confirmed official Hebrew and English terminology.
- Mourning days: double-confirmed paid mourning absence framework and seven-calendar-day default warning.
- APIs/webhooks: double-confirmed as not applicable for this local tracker.

## [1.1.0] - 2026-06-03

### Added

- Added installable `leave_sick_day_tracker` package with normal imports.
- Added neutral-content audit report and Hebrew quality-assurance log.
- Added command-line create and event commands that support response chaining.

### Changed

- Replaced hyphenated Python filenames with underscored entry points.
- Updated Hebrew localization to DD/MM/YYYY and professional Israeli terminology.
- Updated development setup to `pip install -e .` plus `pip install -r requirements-dev.txt`.

### Fixed

- Removed dynamic import loading from the command-line tool.
- Confirmed public Markdown has no external visual marks or emoji.

The format follows Keep a Changelog, and versioning follows semantic versioning.

## [1.0.0] - 2026-06-03

### Added

- Comprehensive English guide with examples, edge cases, Mermaid decision trees, troubleshooting, anti-patterns, and production checklist.
- Comprehensive Hebrew guide with Israeli terminology, ₪/`DD/MM/YYYY` localization guidance, and practical workflows.
- Regulatory/reference guide for Israeli annual leave, sick leave, miluim, parental leave, mourning days, workweek handling, and local data contracts.
- End-to-end workflow guide for setup, payroll close, miluim, sick leave, parental leave, mourning days, year-end review, and corrections.
- Troubleshooting reference for balance, import, legal-review, command-line tool, and audit issues.
- Test scenario reference with 30 concrete cases.
- Migration checklist for spreadsheet and payroll export cutovers.
- Typed sync/async Python client for local calculations.
- Click-based command-line tool for templates, entitlement, sick pay, validation, summaries, and built-in scenario.
- Pytest suite with more than 20 passing tests.
- Five runnable examples.
- README, MIT license, `pyproject.toml`, and `requirements-dev.txt`.

### Changed

- Replaced the stub content with a production-ready neutral package.
- Bumped package version from `0.1.0` to `1.0.0`.
- Expanded metadata tags and supported use cases.
- Removed contributor metadata and distribution callouts.

### Removed

- Stub-only descriptions.
- Any contributor field.
- Any visual asset or image reference.
