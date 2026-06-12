# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog conventions, and this package uses semantic versioning.

## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation, official URLs, access date, short source snippets, and summary counts.
- Added web-validated official source notes to `references/api-reference.md`.
- Added VAT handling guidance confirmed against Israeli official sources for 2026.

### Changed

- Refined WhatsApp voice-message guidance to prefer OGG audio encoded with OPUS for Business Platform voice-message integrations.
- Clarified that the package has no hosted API endpoint, webhook listener, or external API host; provider calls remain local and command-based.
- Expanded Hebrew QA log with the web-validation terminology pass.

### Verified

- Pass 1 and Pass 2 confirmed Israeli VAT at 18% from 01/01/2025 using Tax Authority, government, and Knesset-related sources.
- Pass 1 and Pass 2 confirmed privacy terminology, database notification duties, data-security levels, and serious-incident reporting references.
- Pass 1 and Pass 2 confirmed WhatsApp audio format, media upload, messages webhook, and optional external endpoint paths.
- Pass 1 and Pass 2 confirmed `he-IL` speech locale support and provider variation for punctuation and speaker labels.

## [2.1.0] - 2026-06-03

### Added

- Added installable `hebrew_voice_to_text` Python package.
- Added `create-job`, `show-job`, and `run-job` command chain with stable local job identifiers.
- Added package-level imports such as `from hebrew_voice_to_text import HebrewVoiceTextClient`.
- Added neutral packaging audit report.
- Added Hebrew QA log with localization and terminology corrections.
- Added `pytest-asyncio` to development requirements.
- Added environment handling for examples and command-line usage.
- Added provider-neutral request builder and result summary methods.

### Changed

- Moved script-oriented client implementation to underscored module name.
- Removed the hyphenated client implementation file.
- Updated README installation commands to use editable install and development requirements.
- Updated quick start to extract a job id from the create response and reuse it in the next command.
- Updated examples to read environment variables and accept `--env sandbox|production`.
- Updated examples to print JSON with `ensure_ascii=False` and indentation.
- Improved Hebrew terminology, currency formatting, and date localization.

### Fixed

- Fixed package importability without path manipulation.
- Fixed command-line JSON output for Hebrew readability.
- Fixed test suite to import the package normally.
- Fixed public Markdown symbol audit.
- Fixed metadata version and script references.

## [2.0.0] - 2026-06-03

### Added

- Added comprehensive English and Hebrew guides.
- Added provider-neutral client and command-line helper.
- Added workflow, troubleshooting, test scenario, and migration references.
- Added README, MIT license, changelog, project metadata, and development requirements.
