# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and the package uses semantic versioning where practical.



## [1.4.0] - 2026-06-04

### Added

- Web-validated two-pass verification log with source URLs, access date, and short quotes.
- Official-source notes for Home Front Command app/portal alert terminology.
- Municipal shelter validation notes for Tel Aviv-Yafo and Jerusalem.
- VAT validation note confirming 18% VAT context as of 2026 for future business-cost extensions.

### Changed

- Corrected package language from nationwide shelter coverage to configured shelter datasets in Israel.
- Corrected alert endpoint documentation: `alerts.json` is now described as an observed, undocumented, configurable endpoint pattern rather than an official public API.
- Updated README and API reference to emphasize official channels and configurable sources.

### Verified

- VAT 18% effective 01/01/2025 was double-confirmed.
- Home Front Command real-time/location-based app alerts were double-confirmed.
- Hebrew terminology for יישומון פיקוד העורף, אמצעי התרעה אישי, מרחב מוגן, and מקלט ציבורי was double-confirmed.
- Privacy treatment of location data and data minimization guidance was double-confirmed.
- No webhook event names apply to this package.

## [1.3.1] - 2026-06-04

### Added

- Branding and author audit report.
- Hebrew quality-assurance log.
- Installable `red_alert_shelter_finder` package with importable client and CLI modules.
- Watch creation and watch checking workflow for chained quick-start examples.
- Environment-aware runnable examples for sandbox and production modes.

### Changed

- Removed hyphenated Python client and CLI files.
- Replaced script-level import hacks with package imports.
- Updated README install instructions to separate `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Hebrew localization to DD/MM/YYYY.
- Expanded development requirements with pytest-asyncio.

### Fixed

- Public Markdown audit removes visual asset, author, and emoji risks.
- CLI runner now uses the installed package module.
- Tests import the installed module directly.

## [1.3.0] - 2026-06-04

### Added

- Comprehensive English guide with examples, edge cases, decision trees, troubleshooting, anti-patterns, and production checklist.
- Full Hebrew guide using natural Israeli professional terminology, DD-MM-YYYY dates, and ₪ examples.
- API and data reference for alert payloads, public shelter datasets, error handling, polling, and regulation categories.
- End-to-end workflow guide for consumers, shops, delivery operations, clinics, kiosks, and developers.
- Dedicated troubleshooting guide.
- Test scenario reference with more than 20 concrete scenarios.
- Migration checklist.
- Typed Python sync and async client.
- Click-based CLI.
- pytest suite with more than 20 tests.
- Runnable examples for alerts, nearest shelters, business procedures, async fetch, and GeoJSON loading.
- MIT license with neutral copyright holder.

### Changed

- Rebuilt package in neutral voice.
- Removed creator metadata.
- Removed branding, visual marks, visual markers, visual headers, and distribution callouts.
- Expanded metadata tags.

### Fixed

- Added explicit distinction between no active alert and unavailable alert feed.
- Added callback-wrapped payload parsing.
- Added Hebrew locality normalization and alias handling.
- Added coordinate validation for Israel-focused shelter lookup.
