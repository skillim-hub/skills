# Changelog

All notable changes to this package are documented here.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-04

### Added

- Added `references/verification-log.md` with Pass 1 and Pass 2 web-validation rows, source URLs, access date, short snippets, and status tags.
- Added web-verified rate snapshots to the English and Hebrew skill guides and to the reference map.
- Added a regression test for the 2026 default minimum wage configuration.

### Changed

- Updated default adult minimum wage configuration to ₪6,443.85 monthly and ₪35.40 hourly on the 182-hour basis, effective 01/04/2026.
- Converted `scripts/hr_compliance_advisor_client.py` into an import shim so the installable package is the single implementation source.
- Documented VAT at 18% from 01/01/2025 as status context only, not as a labor-law classification test.
- Clarified overtime caps, pension contribution defaults, travel reimbursement, convalescence pay, parental protections, and contractor-status source checks.

### Fixed

- Corrected stale minimum wage defaults discovered during Pass 1 and double-confirmed during Pass 2.
- Updated affected tests and examples so the suite passes with the 2026 defaults.

## [2.1.0] - 2026-06-04

### Added

- Added installable `hr_compliance_advisor` package exports for direct Python imports.
- Added local case creation and case review flow for command-line quick starts.
- Added neutrality audit report and Hebrew quality-assurance log.

### Changed

- Replaced the hyphenated client script with `scripts/hr_compliance_advisor_client.py`.
- Updated examples to read environment variables, accept `--env sandbox|production`, and print UTF-8 JSON with indentation.
- Updated development installation instructions to use editable installation before test dependencies.
- Updated Hebrew localization to use `DD/MM/YYYY`, Israeli terminology, and imperative phrasing.

### Fixed

- Removed file-location import loading from tests and examples.
- Confirmed syntax with `compileall` and behavior with pytest.

## [2.0.0] - 2026-06-03

### Added

- Expanded English and Hebrew skill guides.
- Added legal source reference, workflow guide, troubleshooting guide, test scenarios, migration checklist, examples, and pytest coverage.
- Added typed synchronous and asynchronous helper classes.

### Changed

- Converted the package into a neutral Israeli HR compliance triage skill.
- Used neutral imperative language throughout public documentation.

### Security

- Added data-minimization guidance for employment, payroll, medical, family-status, and identity records.
