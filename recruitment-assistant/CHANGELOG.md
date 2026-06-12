# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [0.4.0] - 2026-06-04

### Added

- Added web-validated `references/verification-log.md` with two independent validation passes for each source-sensitive row.
- Added verified-source notes to the API reference covering VAT limits, local-only operation, score thresholds, and scheduling defaults.

### Changed

- Confirmed the Israeli standard VAT rate as 18% from 01/01/2025 using official sources; kept all VAT usage contextual only.
- Double-confirmed equal-opportunity, privacy, disability, pregnancy, fertility-treatment, reserve-duty, and job-ad-discrimination guardrails against Israeli public sources.
- Reworded scheduling guidance from an absolute Israeli workweek statement to a conservative Sunday to Thursday default with documented exceptions.
- Clarified that Hebrew and English resume handling is a package capability, not a statutory requirement.

### Fixed

- Removed static holiday placeholder dates from the scheduler to avoid presenting unverified Jewish-holiday dates.
- Updated README, SKILL.md, SKILL_HE.md, workflow guide, troubleshooting, and test scenarios after second-pass scheduling validation.

## [0.3.0] - 2026-06-04

### Added

- Added branding audit report.
- Added Hebrew QA log.
- Added installable `recruitment_assistant` Python package.
- Added underscored client and CLI script entry files.
- Added environment-aware runnable examples.
- Added CLI commands for screening, batch ranking, job-ad validation, scheduling, and version output.
- Added tests for synchronous and asynchronous workflows, compliance checks, scheduling, and localization.

### Changed

- Replaced the hyphenated Python client filename with an underscored filename.
- Updated README installation to use editable install and development requirements.
- Updated quick-start flow to extract a candidate identifier before reuse.
- Updated public Markdown to remove visual decoration and keep neutral presentation.
- Updated Hebrew guidance for professional Israeli terminology, ₪, and DD/MM/YYYY.

### Fixed

- Fixed package import behavior so `from recruitment_assistant import ...` works after installation.
- Fixed examples to use `json.dumps(..., ensure_ascii=False, indent=2)`.
- Fixed development requirements to include `pytest-asyncio`.

## [0.2.0] - 2026-06-03

### Added

- Added bilingual operating guides.
- Added workflow, troubleshooting, test-scenario, and migration reference files.
- Added local client, CLI draft, examples, and pytest coverage.

## [0.1.0] - 2026-06-03

### Added

- Initial neutral recruitment assistant package.
