# Changelog


## [2.1.0] - 2026-06-03

### Added

- Added `references/verification-log.md` with two-pass web validation, source URLs, access date, and short source snippets.
- Added validated 2026 reference values for VAT, exempt dealer threshold, Israel Invoices allocation thresholds, WhatsApp endpoint defaults, webhook names, spam-law compensation, accessibility, consumer price display, and privacy/security references.
- Added configurable constants: `DEFAULT_VAT_RATE`, `DEFAULT_EXEMPT_DEALER_THRESHOLD_ILS_2026`, and `ISRAEL_INVOICES_THRESHOLD_ILS_FROM_2026_06_01`.

### Changed

- Bumped package metadata to version `2.1.0`.
- Corrected WhatsApp positioning from a broad dominance claim to a verified "highly adopted WhatsApp-first channel" operating assumption.
- Updated documentation to cite the 18% VAT default as web-validated as of 03/06/2026 and configurable before production.
- Added 2026 Israel Invoices thresholds: 10,000 ₪ before VAT from 01/01/2026 and 5,000 ₪ before VAT from 01/06/2026.
- Added 2026 exempt dealer threshold reference: 122,833 ₪.
- Clarified WhatsApp Business Platform endpoint defaults: `https://graph.facebook.com`, `POST /{PHONE_NUMBER_ID}/messages`, `messages`, `statuses`, and `message_template_status_update`.

### Pass 1 findings

- VAT increase effective 01/01/2025 confirmed from Knesset publication.
- Israeli data security regulation reference confirmed from the Privacy Protection Authority.
- Consumer price display rule confirmed from the Consumer Protection Authority.
- Accessibility requirement for public internet services confirmed from the Commission for Equal Rights of Persons with Disabilities.
- WhatsApp Business Platform Graph API and webhook references confirmed from Meta documentation.
- Israel Invoices and exempt dealer threshold references found in Tax Authority sources.

### Pass 2 findings

- VAT rate still current in 2026 double-confirmed from PwC Worldwide Tax Summaries.
- Exempt dealer threshold double-confirmed from a second Tax Authority page.
- Israel Invoices thresholds double-confirmed from Tax Authority/Govextra and FAQ sources.
- Spam-law consent and compensation references double-confirmed from Knesset, Privacy Protection Authority, Kol Zchut, and Supreme Court materials.
- WhatsApp adoption claim corrected: sources support very high adoption, but not an official state classification of channel dominance.



## [2.0.1] - 2026-06-03

### Added

- Added branding, author, logo, and image audit report.
- Added Hebrew QA log for terminology, tone, and localization corrections.
- Added importable `lead_qualification_bot` package.
- Added `create` and `get` commands for a chained quick-start flow.
- Added environment selection for sandbox and production in the command line interface and examples.

### Changed

- Moved the real client implementation to importable underscored modules.
- Removed the hyphenated client file.
- Updated README installation instructions to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated localization references from DD-MM-YYYY to DD/MM/YYYY.
- Updated examples to read environment variables and print JSON with `ensure_ascii=False` and `indent=2`.
- Updated packaging configuration so `from lead_qualification_bot import LeadQualificationClient` works after installation.

### Verified

- Ran branding and author grep audit.
- Ran public Markdown emoji and image-reference checks.
- Ran pytest.
- Ran `python -m compileall scripts/ -q`.


All notable changes are documented here. The format follows Keep a Changelog and semantic versioning.

## [2.0.0] - 2026-06-03

### Added

- Comprehensive English and Hebrew guides.
- Israeli API, workflow, troubleshooting, scenario, and migration references.
- Typed sync/async Python client.
- Full Typer CLI.
- pytest suite with more than 20 tests.
- Five runnable examples and sample CSV.
- MIT license, packaging configuration, and development requirements.

### Changed

- Refactored to a neutral, implementation-focused voice.
- Expanded metadata tags and version.
- Adapted flows for Hebrew WhatsApp lead qualification in Israel.

### Removed

- Non-neutral attribution metadata.
- Decorative or promotional material.
- Distribution-oriented language.
