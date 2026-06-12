# Changelog

All notable changes to this skill are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [2.2.0] - 2026-06-03

### Added

- Two-pass web validation log in `references/verification-log.md`.
- Live-source notes for VAT, WhatsApp Business Platform, Israel Post tracking, PCI DSS, privacy, accessibility, consumer protection, marketing consent, and payment-system context.
- Summary table showing 23 checks, 18 double-confirmed checks, 5 corrected checks, and 0 final unconfirmed checks.

### Changed

- Corrected `references/api-reference.md` title and API wording.
- Corrected `PCDSS` to `PCI DSS`.
- Clarified that `/api/orders`, `/api/tracking`, `/api/payments/link`, `/api/accounting/documents`, and `/api/support/tickets` are internal placeholder endpoints.
- Clarified that WhatsApp `messages` webhook terminology is official, while package error names are normalized internal names.
- Added verified VAT note: general Israeli VAT rate is 18% from 01/01/2025, but VAT treatment remains delegated to accounting-system configuration and professional review.
- Bumped metadata version to 2.2.0.

### Web validation findings

- Pass 1 confirmed the VAT rate through Israel Tax Authority terminology and VAT history pages.
- Pass 2 confirmed the VAT rate through a 2026 government document and Knesset VAT-rate change notice.
- Pass 1 confirmed consumer cancellation guidance through the Consumer Protection Authority return page.
- Pass 2 confirmed consumer-protection legal context through State Comptroller and Knesset/legal regulation sources.
- Pass 1 confirmed privacy data-security regulations through the English Privacy Protection Authority page.
- Pass 2 confirmed privacy terminology through the Hebrew Privacy Protection Authority page.
- Pass 1 confirmed service/web accessibility through the English accessibility page.
- Pass 2 confirmed Hebrew accessibility terminology through the Hebrew website-accessibility and service-accessibility pages.
- Pass 1 confirmed anti-spam consent through the Ministry of Communications FAQ.
- Pass 2 confirmed advertising-message consent through the Privacy Protection Authority marketing page.
- Pass 1 confirmed payment-services law through the Bank of Israel legislation page.
- Pass 2 confirmed payment-system oversight through the Bank of Israel payment-system legislation page.
- Pass 1 found a PCI DSS typo in the package.
- Pass 2 confirmed PCI DSS terminology and cardholder-data wording through PCI SSC sources.
- Pass 1 confirmed WhatsApp 24-hour window, templates, and escalation path through WhatsApp Business policy.
- Pass 2 confirmed WhatsApp template use and webhook terminology through Meta developer documentation.
- Pass 1 confirmed Israel Post public tracking wording.
- Pass 2 confirmed Israel Post item-trace details and customs parcel-tracing context.
- Pass 1 and Pass 2 confirmed the customer-service claim as an implementation pattern, not a regulatory guarantee: FAQ automation handles routine questions while humans handle complex or high-risk cases.


## [2.1.0] - 2026-06-03

### Added

- Branding, author, logo, badge, and public Markdown audit report.
- Hebrew QA log with terminology, date format, and prose corrections.
- Installable `customer_service_chat_agent` Python package.
- Underscored client and CLI script names.
- CLI ticket creation and status commands for quick-start chaining.
- Environment-aware runnable examples that read environment variables.
- Additional tests for importability, ticket creation, CLI commands, and DD/MM/YYYY formatting.

### Changed

- Replaced hyphenated Python script imports with importable package usage.
- Updated README installation instructions to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Israeli date localization from DD/MM/YYYY to DD/MM/YYYY.
- Updated pyproject packaging configuration so `from customer_service_chat_agent import ...` works after installation.
- Bumped metadata version to 2.1.0.

### Removed

- Hyphenated client and CLI files from the active script layout.
- Any remaining public Markdown emoji, badge, logo, and banner references found during audit.


## [2.0.0] - 2026-06-03

### Added

- Comprehensive English and Hebrew guides.
- Israeli APand regulatory reference with request/response examples and error tables.
- End-to-end workflow guide.
- Troubleshooting guide.
- 30 test scenarios.
- Migration checklist.
- Typed sync and async Python client.
- Typer CLI.
- Pytest suite with more than 20 tests.
- Runnable examples.
- README, MIT license, pyproject, and development requirements.

### Changed

- Refactored into a neutral, brand-free, logo-free package.
- Bumped metadata version to 2.0.0.
- Expanded tags and Israeli localization.

### Removed

- Author metadata.
- Branding, badges, banners, logos, image references, and distribution callouts.
