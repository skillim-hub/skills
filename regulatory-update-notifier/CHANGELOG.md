# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-02

### Added

- Two-pass web verification log for official Israeli sources, snippets, URLs, access date, endpoint paths, terminology, rates, thresholds, and source availability caveats.
- Government Legislation Site (`tazkirim.gov.il`) as an explicit public-consultation source.
- Current validated Tax Authority baseline for VAT and Israel Invoice allocation thresholds.
- Web validation scenarios covering stale rates, geo-blocked Knesset OData responses, public consultation deadlines, mid-year tax thresholds, and unverified example values.

### Changed

- Updated the source reference with validated official URLs, access date, no-webhook guidance, Knesset OData geo-block handling, and a current rates-and-thresholds table.
- Reworded public guide examples so unverified monetary thresholds are not presented as official values.
- Replaced the script client duplicate with a compatibility wrapper around the installable package.
- Expanded migration, troubleshooting, workflow, and Hebrew QA references with web-validation guidance.

### Verified

- Pass 1 confirmed VAT history, Knesset OData service family, Reshumot pages, authority pages, public consultations, tax service thresholds, official terminology, and absence of confirmed webhook names for monitored sources.
- Pass 2 rechecked every confirmed row with a different query or source where possible and corrected one unverified illustrative threshold in public guides.

## [2.1.0] - 2026-06-02

### Added

- Branding and attribution audit report.
- Hebrew quality review log.
- Installable `regulatory_update_notifier` package.
- Profile creation flow with stable id chaining for CLI quick start.
- Sandbox and production environment option across CLI and examples.
- Development requirement for asynchronous tests.
- Underscored client implementation mirror for script-based workflows.

### Changed

- Replaced file-loading imports with normal package imports.
- Updated README installation to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Hebrew localization to `DD/MM/YYYY`.
- Updated examples to read environment variables and print JSON with `ensure_ascii=False` and indentation.
- Updated tests to import the installable package directly.

### Removed

- Hyphenated client module.
- Any remaining public documentation references that could be interpreted as visual branding, status graphics, header images, visual marks, or attribution callouts.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English skill guide with decision trees, examples, edge cases, troubleshooting, anti-patterns, and production checklist.
- Comprehensive Hebrew guide using Israeli professional terminology, ₪ amounts, and date localization.
- Israeli source and endpoint reference covering Knesset, Reshumot, gov.il authority pages, consultation sources, and key regulators.
- End-to-end workflow guide for freelancers, ecommerce, Reshumot confirmation, consultations, employers, and consumers.
- Troubleshooting reference.
- Thirty concrete test scenarios.
- Migration checklist.
- Typed sync and async Python client.
- Typer CLI.
- Pytest suite with more than twenty tests.
- Runnable example scripts.
- Project metadata, development requirements, MIT license, and README.

### Changed

- Refocused the package on general Israeli regulatory update monitoring for small businesses, freelancers, and consumers.
- Replaced sector-only logic with broad legal and regulatory monitoring.
- Expanded source classification and relevance scoring.

### Removed

- Credit metadata.
- Branding, visual assets, external image references, and distribution callouts.
