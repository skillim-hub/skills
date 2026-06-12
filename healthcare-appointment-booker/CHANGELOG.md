# Changelog

All notable changes to this skill are documented in this file.

The format is based on Keep a Changelog, and this project follows semantic versioning.

## [2.2.0] - 2026-06-04

### Added
- Two-pass web validation log with pass 1 and pass 2 sources per check.
- Web-validated operational notes for HMO appointment channels, VAT, emergency routing, privacy, accessibility, and consumer pricing.
- Maccabi same-specialty continuity caveat in English and Hebrew guidance.
- Additional test scenario for Maccabi same-specialty continuity blocking.

### Changed
- Updated business pricing examples to mention the 18% VAT rate verified on 04/06/2026 and clarify that VAT applies only where legally required.
- Updated official Ministry of Health hotline reference to Kol Habriut 5400*.
- Clarified that no public cross-HMO appointment-booking API endpoints or webhook event names were confirmed.

### Verified
- Pass 1 confirmed current VAT, HMO appointment channels, Ministry of Health references, privacy, accessibility, consumer price disclosure, and MDA 101 emergency routing.
- Pass 2 double-confirmed the same rows using different official or corroborating sources where available.
- One row was corrected after pass 1 by adding Maccabi’s same-specialty continuity rule and call-center fallback.

## [2.1.0] - 2026-06-04

### Added
- Branding and attribution audit report.
- Hebrew quality assurance log.
- Importable package interface for `from healthcare_appointment_booker import ...`.
- Root-level underscored client module for `from healthcare_appointment_booker_client import ...`.
- CLI create/show flow with id extraction support.
- Environment-aware example scripts with sandbox and production modes.

### Changed
- Replaced hyphenated client module with underscored importable module.
- Updated README install steps to use editable install and separate development requirements installation.
- Updated Hebrew dates to DD/MM/YYYY.
- Updated Hebrew terminology to use natural professional Hebrew and reduce unnecessary foreign terms.
- Updated CLI and tests to avoid dynamic file imports and path manipulation.
- Bumped metadata version to 2.1.0.

### Verified
- Ran branding and attribution audit.
- Ran public Markdown emoji scan.
- Ran Hebrew niqqud scan.
- Ran pytest.
- Ran Python compile check for scripts.

## [2.0.0] - 2026-06-04

### Added
- Comprehensive English guide with decision trees, edge cases, anti-patterns, troubleshooting, and production checklist.
- Comprehensive Hebrew guide using Israeli professional terminology, pricing examples in ₪, and localized dates.
- Israeli official-channel and regulatory reference.
- End-to-end workflow guide.
- Dedicated troubleshooting reference.
- Concrete test scenarios.
- Migration checklist for older booking workflows.
- Typed Python client with sync and async methods.
- Typer CLI.
- Runnable example scripts.
- Pytest suite with more than 20 tests.
- MIT license.
- Python project metadata and development requirements.

### Changed
- Refactored appointment booking as a privacy-preserving official-channel workflow.
- Improved specialist routing and referral/order handling.
- Added emergency escalation before routine booking.

### Removed
- Visual identity references, attribution metadata, and distribution callouts.
- Unsafe patterns implying credential capture, scraping, or portal bypass.
