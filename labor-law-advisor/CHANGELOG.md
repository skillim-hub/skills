# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, access date, and short source snippets.
- Added dated verification notes for VAT, minimum wage, overtime, workweek, severance, Section 14, parental rights, Form 355, and collective agreement sources.
- Added CLI case persistence through `.labor-law-advisor-cases.json` or `LABOR_LAW_ADVISOR_CASE_STORE` for chained local workflows.

### Changed

- Confirmed the 01/04/2026 adult minimum wage default at ₪6,443.85 monthly and ₪35.40 hourly on the 182-hour basis.
- Confirmed the 18% Israeli VAT rate effective 01/01/2025 and still current in 2026 for invoice-context workflows.
- Clarified that the 8.6 daily overtime threshold is a common 5-day regular-day example, not a universal threshold.
- Corrected README quick-start command chaining so the created case identifier is read from standard input and used in the next step.
- Removed remaining direct-execution `sys.path` hacks from public example scripts and the executable CLI wrapper.
- Bumped package metadata and project version to 2.2.0.

### Fixed

- Fixed the cross-process CLI case-summary workflow by persisting `create-case` output in a local JSON case store.

### Web validation findings

- Pass 1 and Pass 2 confirmed VAT at 18% from 01/01/2025 and current in 2026.
- Pass 1 and Pass 2 confirmed adult minimum wage from 01/04/2026 at ₪6,443.85 monthly and ₪35.40 hourly on the 182-hour basis.
- Pass 1 and Pass 2 confirmed the 186-hour hourly minimum wage comparison figure at ₪34.64.
- Pass 1 and Pass 2 confirmed the 42-hour private-sector workweek baseline.
- Pass 1 and Pass 2 confirmed the common 8.6-hour daily threshold example for regular days in a 5-day week, with schedule-specific caveats.
- Pass 1 and Pass 2 confirmed weekday overtime premiums of 125% for the first two overtime hours and 150% afterward.
- Pass 1 and Pass 2 confirmed that rest-day or holiday overtime can require combined 175% and 200% rates.
- Pass 1 and Pass 2 confirmed the severance baseline of one monthly wage per year for monthly workers, subject to exceptions.
- Pass 1 and Pass 2 confirmed that a valid Section 14 arrangement with 8.33% monthly severance deposits can cover full severance liability.
- Pass 1 and Pass 2 confirmed the mandatory 6% severance component reference for pension/severance checks.
- Pass 1 and Pass 2 confirmed National Insurance maternity allowance periods of 15 weeks/105 days and 8 weeks/56 days.
- Pass 1 and Pass 2 confirmed Form 355 as the National Insurance maternity allowance claim form.
- Pass 1 and Pass 2 confirmed Form 161 as the Tax Authority retirement and termination reporting form.
- Pass 1 and Pass 2 confirmed that dismissal or scope/income reduction in pregnancy may require a Ministry permit after 6 months.
- Pass 1 and Pass 2 confirmed the professional term `שעת הורות` and the 174-hour/4-month parenting-hour rule.
- Pass 1 and Pass 2 confirmed the Ministry collective agreements database as the primary check for collective agreements.
- Pass 1 and Pass 2 confirmed the legal concept of collective agreements and extension orders.
- Pass 2 corrected the local chained CLI workflow by persisting created case records and fixing the README shell extraction command.

## [2.1.0] - 2026-06-02

### Changed

- Moved the real client implementation to `scripts/labor_law_advisor_client.py` and removed the hyphenated client module.
- Added installable package configuration for editable installs and direct imports.
- Updated README installation and chained quick-start commands.
- Updated examples to accept `--env sandbox|production`, read environment variables, and print localized JSON.
- Localized Hebrew dates to DD/MM/YYYY and logged Hebrew QA decisions.

### Added

- Added branding audit report.
- Added public-method count support through the verification pass.

## [2.0.0] - 2026-06-02

### Added

- Expanded English `SKILL.md` with intake flow, examples, decision trees, edge cases, anti-patterns, troubleshooting, safety boundaries, and production checklist.
- Expanded Hebrew `SKILL_HE.md` with natural Israeli professional terminology, ₪ formatting, and DD/MM/YYYY dates.
- Added `references/api-reference.md` for official Israeli source hierarchy, local helper interface, request/response examples, and error table.
- Added `references/workflow-guide.md` with end-to-end workflows for minimum wage, overtime, severance, parental rights, Histadrut/collective checks, freelancer classification, household workers, and payroll launch.
- Added `references/troubleshooting.md`.
- Added `references/test-scenarios.md` with 30 concrete scenarios.
- Added `references/migration-checklist.md`.
- Added typed sync/async Python helper at `scripts/labor_law_advisor_client.py`.
- Added Typer CLI at `scripts/labor_law_advisor_cli.py`.
- Added pytest suite with more than 20 tests.
- Added runnable example scripts.
- Added `README.md`, `LICENSE`, `pyproject.toml`, and `requirements-dev.txt`.

### Changed

- Renamed package scope to `labor-law-advisor`.
- Bumped metadata version to `2.0.0`.
- Reworked content toward small businesses, freelancers, employees, and consumers.
- Replaced single-purpose severance calculator with broader calculation and triage helper.

### Removed

- Removed attribution metadata.
- Removed visual assets and distribution-specific callouts.
