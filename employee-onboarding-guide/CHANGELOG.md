# Changelog

All notable changes to this package are documented in this file. The format follows Keep a Changelog, and the package uses semantic versioning.


## [2.2.0] - 2026-06-04

### Added

- Web-validated verification log with two-pass source checks and access date.
- 2026 reference notes for VAT, National Insurance brackets, health insurance rates, and pension timing.
- Explicit statement that the helper is local-only and uses no external API endpoint or webhook event.

### Changed

- Corrected Form 101 guidance to include submission within 7 days of starting work and annual renewal.
- Corrected employment terms notice timing to 30 days for adult employees and 7 days for employees under 18.
- Expanded pension guidance for 6-month waiting period and prior-coverage retroactive timing.
- Expanded foreign-worker checks to include medical insurance, written contract, suitable housing, and pension or deposit route.
- Expanded timekeeping guidance for daily employee signature and responsible-manager approval when records are not electronic, digital, or mechanical.
- Expanded Hebrew guidance using DD/MM/YYYY localization and official Israeli terminology.

### Verified

- VAT standard rate confirmed as 18% from 01-01-2025 and still used by 2026 official references.
- National Insurance 2026 reduced bracket confirmed at ₪7,703 and maximum contribution income at ₪51,910.
- Health insurance salaried-employee deduction rates confirmed at 3.23% and 5.17%, with bracket caveat.
- Prevention of sexual harassment employer duties confirmed, including policy requirement for employers with more than 25 employees.
- Privacy and remote-work monitoring guidance confirmed against the Privacy Protection Authority.

## [2.1.0] - 2026-06-04

### Added

- Branding audit report.
- Hebrew QA log.
- Installable underscored client module.
- Typer CLI module with local create, validate, checklist, message, and sample commands.
- Quick-start flow that extracts the created record id and reuses it.
- Example scripts that read environment variables and accept `--env sandbox|production`.
- Date normalization for English DD-MM-YYYY and Hebrew DD/MM/YYYY.
- Compile check requirement.

### Changed

- Removed the hyphenated client script.
- Updated imports to use `employee_onboarding_guide_client`.
- Updated README installation to include `pip install -e .`.
- Added `pytest-asyncio` to development requirements.
- Updated Hebrew prose to use DD/MM/YYYY.
- Improved local JSON responses with `ensure_ascii=False` formatting.

### Fixed

- Package can be imported after editable installation.
- CLI record creation can chain into checklist generation by id.
- Public Markdown contains no emoji, status-link artifacts, image references, or visual assets.

## [2.0.0] - 2026-06-04

### Added

- Comprehensive English guide.
- Hebrew guide.
- Regulation reference.
- Workflow guide.
- Troubleshooting guide.
- Test scenarios.
- Migration checklist.
- Python helper, CLI, examples, tests, README, license, project metadata, and development requirements.

### Removed

- Author metadata and non-neutral wording.
