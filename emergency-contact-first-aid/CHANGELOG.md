# Changelog

All notable changes are documented in this file.

The format follows Keep a Changelog conventions. Versioning follows semantic versioning where practical.

## [2.2.0] - 04-06-2026

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, access date, and short quoted snippets.
- Added MDA written emergency access number `052-7000-101` to defaults, templates, and public references.
- Added United Hatzalah `1221` as a verified volunteer responder contact while preserving `101` as primary medical dispatch.
- Added explicit non-applicable notes for remote API hosts, endpoint paths, webhook names, official forms, fee schedules, and VAT calculations.

### Changed

- Bumped version to `2.2.0`.
- Updated Hebrew AED terminology to `מפעם (דפיברילטור)` based on official MDA wording.
- Rephrased Hatzalah-related claims to avoid implying that the package reproduces restricted responder protocols.
- Documented VAT as a verified non-operational fact rather than a package feature.

### Verified

- Double-confirmed Israeli emergency numbers 100, 101, 102, 103, 104, 106/107, MDA written access, and United Hatzalah 1221.
- Double-confirmed CPR compression rate 100-120 per minute, burn cooling for 20 minutes, stroke 101/FAST timing, anaphylaxis 101/epinephrine guidance, and severe bleeding direct pressure.
- Double-confirmed privacy, data-security, patient-confidentiality, and accessibility reference areas.

## [2.1.0] - 04-06-2026

### Added

- Branding audit report.
- Hebrew quality assurance log.
- Installable Python package under `src/emergency_contact_first_aid`.
- Console command entry point for `emergency-contact-first-aid`.
- Profile creation command that returns a local profile id.
- Quick-start flow that extracts the profile id from the create response and reuses it.
- Environment-aware examples with `--env sandbox` and `--env production`.
- `pytest-asyncio` in development requirements.
- Syntax verification using `compileall`.

### Changed

- Replaced hyphenated client file with underscored client script name.
- Updated imports to use the installable module.
- Updated Hebrew localization to `DD/MM/YYYY` in Hebrew-facing material.
- Expanded privacy checks and redaction behavior.
- Cleaned package output to exclude cache and bytecode artifacts.

### Removed

- Hyphenated client script from the v2 bundle.
- Runtime cache directories from the archive.
- Badge, logo, banner, and image references.

## [2.0.0] - 04-06-2026

### Added

- English and Hebrew operational guides.
- Local profile schema, templates, client, CLI, examples, and tests.
- Workflow, troubleshooting, test scenario, and migration references.
