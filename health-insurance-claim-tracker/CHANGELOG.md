# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [1.2.0] - 2026-06-04

### Added

- Web-validated `references/verification-log.md` with two-pass checks for Israeli VAT, SHABAN terminology, Har HaBituach, Capital Market tools, claim-settlement references, privacy, medical-record access, electronic signatures, Tax Authority invoice guidance, and non-API scope.
- Official-source URL table in `references/api-reference.md`.
- VAT, Israel Invoice, and non-API cautions in English and Hebrew guides.
- Business workflow for VAT and Israel Invoice review without tax calculation.

### Changed

- Bumped package version to 1.2.0.
- Updated README file index and environment-variable table.
- Updated examples to allow scenario values through environment variables.

### Verified

- Pass 1 confirmed 17 rows from official or authoritative source snippets.
- Pass 2 re-checked the same 17 rows with different sources where possible.
- No pass-2 factual corrections were required.
- Final verification status: 17 double-confirmed rows, 0 corrected rows, 0 unconfirmed rows.

## [1.1.0] - 2026-06-04

### Added

- Installable `health_insurance_claim_tracker` package.
- Typed synchronous and asynchronous claim tracker clients.
- Typer-based command line interface.
- Underscored compatibility modules under `scripts/`.
- Expanded English and Hebrew operating guides.
- Branding audit report.
- Hebrew quality-assurance log.
- Troubleshooting reference.
- Test scenarios reference with more than 20 concrete cases.
- Migration checklist.
- Six runnable scenario scripts.
- Pytest suite with asynchronous tests.
- Development configuration in `pyproject.toml` and `requirements-dev.txt`.

### Changed

- Replaced hyphenated client filename with underscored import-safe modules.
- Updated README installation instructions to use editable install and development requirements.
- Updated quick start to extract the created claim id and reuse it in the next command.
- Localized Hebrew examples with ₪ and `DD/MM/YYYY`.
- Removed public Markdown emoji, badge links, logo references, and attribution language.

### Fixed

- Package imports now work with `from health_insurance_claim_tracker import ...` without path modifications.
- Examples now read environment variables, accept `--env sandbox|production`, and print JSON with UTF-8 output.
- Tests compile and pass after package layout correction.

## [1.0.0] - 2026-06-04

### Added

- Initial enhanced claim tracker package with bilingual documentation, references, scripts, examples, tests, metadata, license, and project files.
