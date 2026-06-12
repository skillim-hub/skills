# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog, and this package uses semantic versioning.

## [2.2.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation, source snippets, URLs, access date, status tags, and a summary table.
- Added web-validated regulatory status notes to the API reference.
- Added explicit no-webhook applicability notes.

### Changed

- Pass 1 and Pass 2 confirmed Israeli VAT context: standard VAT is 18% from 01/01/2025; documentation now states this as maintained context rather than classifier logic.
- Pass 1 and Pass 2 confirmed VAT effective-date handling; finance routing remains mandatory.
- Pass 1 and Pass 2 confirmed Protection of Privacy Law terminology and Amendment 13 effective-context guidance.
- Pass 1 and Pass 2 confirmed Protection of Privacy Regulations (Data Security), 5777-2017.
- Pass 1 and Pass 2 confirmed transfer-abroad guidance under the Privacy Protection Regulations, 5761-2001.
- Pass 1 and Pass 2 confirmed Communications Law Section 30A spam and unsubscribe terminology.
- Pass 1 and Pass 2 confirmed the statutory 1,000 NIS spam-compensation ceiling; package keeps it outside automated reply logic.
- Pass 1 and Pass 2 confirmed consumer cancellation and refund routing sources.
- Pass 1 and Pass 2 confirmed service-accessibility regulation naming.
- Pass 1 and Pass 2 confirmed data.gov.il CKAN `datastore_search` examples.
- Pass 1 confirmed Bank of Israel quick exchange-rate API; Pass 2 added the newer official series-database API path.
- Pass 1 and Pass 2 confirmed representative exchange-rate context is non-binding unless parties agree otherwise.
- Pass 1 and Pass 2 confirmed Hebrew sentiment/NLP ecosystem support; package wording now clarifies that the bundled analyzer is deterministic and does not ship a pretrained model.
- Pass 1 and Pass 2 confirmed business-messaging insight relevance while preserving platform independence.
- Pass 1 and Pass 2 confirmed webhook event names are not applicable to this package.

### Fixed

- Replaced remaining public documentation examples using dash-form Israeli dates with slash-form `DD/MM/YYYY` examples.
- Corrected the changelog localization note from `DD-MM-YYYY` to `DD/MM/YYYY`.

## [2.1.0] - 2026-06-03

### Changed

- Moved the real client implementation into the importable underscored module.
- Removed the hyphenated client script and updated imports.
- Added a create-response chaining helper for quick-start workflows.
- Added branding and Hebrew quality audit logs.
- Updated development requirements with async test support.

### Fixed

- Removed path-based dynamic imports from examples and tests.
- Updated installation instructions to use editable installation and development requirements.

## [2.0.0] - 2026-06-03

### Added

- Added comprehensive English skill guide with examples, edge cases, mermaid decision trees, anti-patterns, troubleshooting, and production checklist.
- Added comprehensive Hebrew skill guide with Israeli professional terminology, ₪ examples, and `DD/MM/YYYY` localization.
- Added Israeli regulatory and optional API reference with request/response examples and error tables.
- Added end-to-end workflow guide for weekly review, unresolved queues, finance triage, bot improvement, vendor sharing, custom intents, dashboards, incident review, cancellation audits, and lead review.
- Added standalone troubleshooting guide.
- Added test scenario library with more than 20 concrete scenarios.
- Added migration checklist for older exports, manual spreadsheets, and previous package structures.
- Added typed synchronous and asynchronous Python client.
- Added Click-based CLI.
- Added pytest suite with more than 20 tests.
- Added six runnable examples.
- Added README, MIT license, pyproject, and development requirements.

### Changed

- Bumped package version to 2.0.0.
- Renamed package root to `chat-data-analyzer`.
- Reworked metadata tags for Hebrew NLP, Israeli small-business operations, privacy-aware analytics, support QA, and chat trend analysis.
- Replaced opaque guidance with concrete schemas, commands, and expected outputs.

### Removed

- Removed legacy package-specific references.
- Removed legacy naming from the enhanced package.

### Security

- Added identifier masking for email, Israeli mobile phone, valid Israeli ID-like values, Luhn-valid card-like values, and URLs.
- Added privacy-conscious workflow guidance for external sharing and dashboards.

## [1.2.0] - Previous package

### Changed

- Previous package contents were used only as source context for the enhanced neutral refactor.
