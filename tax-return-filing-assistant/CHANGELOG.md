# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.


## [2.2.0] - 2026-06-01

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, access date, short snippets, status tags, and summary counts.
- Added web-validated operating facts to `references/api-reference.md` for VAT, Forms 1301, 135, 126, 856, 6111, and non-API workflow boundaries.

### Changed

- Pass 1 finding: confirmed Israel VAT increased from 17% to 18% effective 01/01/2025 and remains 18% in 2026; kept VAT as reconciliation context only.
- Pass 1 finding: confirmed Form 1301 tax year 2025 online deadline is 30/06/2026; retained date as an official 2025 override.
- Pass 1 finding: found v2 used a generic 31/05 non-online Form 1301 planning date; corrected tax year 2025 to 29/05/2026.
- Pass 1 finding: found v2 used 30/04 for Forms 126 and 856; corrected tax year 2025 to 31/05/2026.
- Pass 1 finding: confirmed Form 135 refund workflow applies only when no full annual return obligation exists and can generally go back six years.
- Pass 1 finding: confirmed Form 6111 threshold remains turnover over ₪300,000 including VAT, subject to exemptions and current-year instructions.
- Pass 2 finding: independently confirmed 18% VAT using a 2026 tax-summary source.
- Pass 2 finding: independently confirmed Form 1301 2025 deadlines using a separate current professional summary and official notice snippets.
- Pass 2 finding: rejected a fixed representative-extension placeholder; replaced it with online statutory planning date unless a verified extension schedule exists.
- Pass 2 finding: independently confirmed Forms 126/856 2025 extension and online approval conditions from payroll/professional summaries that quote the Tax Authority circular.
- Pass 2 finding: confirmed no public unauthenticated submission API or webhook event model for the covered forms; preserved offline helper architecture.

### Fixed

- Updated tests, examples-facing deadline output, SKILL.md, SKILL_HE.md, workflow references, and scenario expectations to match the web-validated 2025 filing dates.
- Updated Hebrew terminology for forms and withholding workflows using official Israeli phrasing.

## [2.1.0] - 2026-06-01

### Added

- Branding, authorship, visual-asset, and emoji audit report.
- Hebrew QA log covering terminology, neutral imperative voice, and DD/MM/YYYY localization.
- Local profile ID store for chained CLI workflows.
- Importable underscore-named Python modules compatible with editable installation.
- CLI commands for creating, listing, reporting from, and deleting local profile IDs.

### Changed

- Replaced hyphenated script-module filenames with underscore-named importable modules.
- Updated README installation flow to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick start so the profile ID from create output is reused in the next command.
- Updated examples to read environment variables, accept `--env sandbox|production`, and emit UTF-8 JSON with stable indentation.
- Updated date rendering to DD/MM/YYYY for Israeli localization.

### Removed

- Path-based import loading from tests and examples.
- Hyphenated Python module filenames that prevented normal imports.

## [2.0.0] - 2026-06-01

### Added

- Comprehensive English guide for Forms 1301, 135, 126, 856, and 6111.
- Comprehensive Hebrew guide with natural Israeli tax terminology and localized formatting.
- Official-source and regulatory reference with local request/response examples.
- End-to-end workflow guide.
- Troubleshooting guide.
- Test scenarios with 30 concrete cases.
- Migration checklist.
- Typed sync and async Python client.
- Click-based CLI.
- Runnable examples.
- Pytest suite with 20+ tests.
- README, MIT license, pyproject, and development requirements.

### Changed

- Refactored package name to `tax-return-filing-assistant`.
- Replaced static form notes with workflow-oriented guidance.
- Added filing-year-aware deadline planning helpers.
- Added privacy and anti-screen-scraping guidance.

### Removed

- Branding, visual marks, organization references, credit metadata, and distribution callouts.
- Distribution callouts.
- Unscoped forms outside the targeted workflows.
