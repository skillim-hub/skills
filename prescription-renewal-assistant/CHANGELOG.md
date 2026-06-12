# Changelog

All notable changes are documented in this file. The format follows Keep a Changelog, and the package uses semantic versioning.

## [2.2.0] - 2026-06-04

### Added

- Two-pass web verification log with source snippets, URLs, access date, and correction status.
- Provider caveats for Be and Newpharm based on live source validation.
- VAT reference note confirming the general Israeli VAT rate as 18% in 2026.
- Official-source notes for Maccabi, Meuhedet, Leumit, Super-Pharm, Ministry of Health, and privacy guidance.
- Additional reference scenarios for Be, Newpharm, VAT, and public API requests.

### Changed

- Updated English and Hebrew guides to stop assuming Be prescription delivery without current app, branch, or pharmacist verification.
- Updated English and Hebrew guides to stop treating Newpharm as a confirmed current Israeli prescription-delivery channel.
- Clarified that provider delivery fees are verification points rather than hardcoded constants.
- Preserved the non-API, human-in-the-loop design because public prescription-renewal endpoints and webhook names were not confirmed.

### Fixed

- Corrected provider wording after skeptical second-pass validation.
- Added final source-backed correction rows for claims that could not be confirmed.

## [2.1.0] - 2026-06-04

### Added

- Branding audit report.
- Hebrew QA log.
- Installable Python package under `prescription_renewal_assistant`.
- Case creation command with reusable case ID.
- Examples that read environment variables and accept `--env sandbox|production`.
- Compile validation step.

### Changed

- Moved real client implementation into the installable package.
- Removed obsolete hyphenated client script.
- Updated README installation commands to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Hebrew documentation to use `DD/MM/YYYY`.
- Updated examples to print JSON with `ensure_ascii=False` and indentation.
- Expanded tests for importability, CLI case chaining, and date localization.

### Fixed

- Eliminated sys.path-based imports from examples and tests.
- Confirmed public Markdown has no emoji, badges, logos, banners, or image references.
- Kept the required neutral MIT license notice.

## [2.0.0] - 2026-06-04

### Added

- English and Hebrew skill guides.
- API-equivalent reference.
- Workflow guide.
- Troubleshooting guide.
- Test-scenarios reference.
- Migration checklist.
- Python helper, CLI, examples, tests, packaging files, and license.

### Removed

- Branding references.
- Logo, badge, banner, and image references.
- Personal credit metadata.
