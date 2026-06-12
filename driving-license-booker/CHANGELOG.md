# Changelog

All notable changes are documented in this file. The format follows Keep a Changelog, and versioning follows semantic versioning.

## [1.3.0] - 2026-06-04

### Added

- Added two-pass web validation log with official-source snippets, source URLs, access date, and pass status.
- Added validated service-link regression tests for driver-license payment, practical-test fee payment, and GoVisit appointment handoff.
- Added VAT handling reminder for private service fees charged by VAT-registered Israeli businesses.

### Changed

- Corrected driver-license payment handoff from vehicle-license route `/voucherspa/input/260` to driver-license route `/voucherspa/input/209`.
- Replaced deprecated appointment host references with GoVisit and the Ministry of Transport appointment information page.
- Reworded practical-test workflow to coordinate through authorized driving teachers or driving schools instead of implying direct official test booking by the package.
- Replaced invalid standalone medical-declaration link with the official driver-license application flow that includes medical declaration guidance.

### Verified

- Double-confirmed 18% Israeli VAT rate for 2026 private-service fee handling.
- Double-confirmed practical-test fee payment route `/voucherspa/input/427` and practical-test workflow boundaries.
- Double-confirmed official terminology for Ministry of Transport and Road Safety, Licensing Division, Licensing Bureau, GoVisit, driver’s license renewal, and practical driving test.
- Confirmed no public official booking API schema or webhook event catalog is referenced by the validated sources.

## [1.2.0] - 2026-06-04

### Added

- Added a full branding, public Markdown, decorative image, and metadata audit report.
- Added Hebrew quality-assurance log with terminology and localization corrections.
- Added installable `src/driving_license_booker` package so `from driving_license_booker import ...` works after editable install.
- Added underscore-named script modules and removed hyphenated Python client files.
- Added CLI examples that read environment variables, accept `--env sandbox|production`, and print JSON with Hebrew-safe formatting.

### Changed

- Updated README install flow to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated quick-start to extract `request_id` from the create response and reuse it in the next command.
- Expanded development dependencies with `pytest-asyncio`.
- Removed generated cache directories from the bundle.

### Fixed

- Removed public Markdown emoji, decorative image references, and legacy branding terms.
- Normalized Hebrew professional terminology, dates, and ₪ formatting.

## [1.1.0] - 2026-06-04

### Added

- Added comprehensive English and Hebrew skill guides.
- Added official-service reference, workflow guide, troubleshooting guide, test scenarios, migration checklist, CLI, client, examples, tests, README, license, and packaging files.

## [1.0.0] - 2026-06-04

### Added

- Initial skill package baseline.
