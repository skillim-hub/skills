# Changelog


## [2.2.0] - 2026-06-02

### Added

- Two-pass web validation log in `references/verification-log.md`.
- VAT note confirming the official Israeli VAT rate as 18% from 01/01/2025, with a warning not to assume recoverable VAT for fines or penalties.
- Source-specific deadline guidance for municipalities and toll operators.
- Explicit statement that no universal public JSON API or official webhook event names were confirmed.
- New web-validated scenarios for API assumptions, VAT treatment, and issuer-specific deadlines.

### Changed

- Clarified that `/fines/lookup`, `/fines/payment-intents`, and `/fines/appeals` are internal middleware examples unless an issuer provides written integration documentation.
- Updated client documentation to say “permitted issuer interfaces or internal middleware” instead of implying public official APIs.
- Expanded README web-validation status.
- Bumped package metadata and project version to `2.2.0`.

### Web validation findings

- Pass 1 confirmed Israel Tax Authority VAT history: `1.1.25 עלה המע"מ ל-18%`.
- Pass 2 confirmed Israel Tax Authority English terminology: `uniform rate of 18% starting from January 1, 2025`.
- Pass 1 confirmed Israel Police online traffic-fine payment.
- Pass 2 confirmed English Israel Police traffic-fine payment wording and support numbers.
- Pass 1 confirmed National Driver Inquiries Center handles police reports only.
- Pass 2 confirmed local authority reports must be addressed to the relevant local authority.
- Pass 1 confirmed Collection Center payment for fines, fees, reports, and debts transferred to collection.
- Pass 2 confirmed debtor scope includes individuals and companies.
- Pass 1 confirmed Tel Aviv online actions for reports.
- Pass 2 confirmed Tel Aviv report topics including cancellation, transfer, court request, information/photo review, and refund.
- Pass 1 confirmed Tel Aviv 30-day cancellation deadline and 90-day court-request deadline.
- Pass 2 corrected the package to treat Tel Aviv 2026 micromobility/₪500 rules as source-specific.
- Pass 1 confirmed other municipalities expose local payment/appeal/status channels.
- Pass 2 confirmed Jerusalem and Netanya examples.
- Pass 1 confirmed Road 6 official invoice payment channels.
- Pass 2 confirmed Road 6 open-charge lookup and account-status wording.
- Pass 1 confirmed Road 6 phishing warning.
- Pass 2 retained the warning and strengthened manual-navigation guidance.
- Pass 1 confirmed Road 6 toll-law terminology.
- Pass 2 confirmed Knesset economic-analysis context for Highway 6 tolls and fines.
- Pass 1 confirmed Carmel Tunnels invoice-payment fields.
- Pass 2 confirmed Carmel personal-area/debt-billing channels.
- Pass 1 confirmed Fast Lane invoice and service channels.
- Pass 2 confirmed Fast Lane 45-day appeal wording.
- Pass 1 confirmed Privacy Protection Authority data-security relevance.
- Pass 2 confirmed current privacy notification and Amendment 13 context.
- Pass 1 confirmed Payment Services Law relevance.
- Pass 2 confirmed government-service exceptions and replacement of the debit-card law.
- Pass 1 found no official public JSON APIs or webhook event names.
- Pass 2 retained the correction: official workflows are portal/form/account based unless separately authorized.


All notable changes are documented in this file.

The format follows Keep a Changelog, and the package follows semantic versioning.

## [2.1.0] - 2026-06-02

### Added

- Branding, author, logo, badge, and emoji audit report.
- Hebrew quality-assurance log.
- Installable `parking_fine_checker` package with importable public API.
- Case creation flow with chained `case_id` usage in README and CLI.
- Environment-aware examples supporting `--env sandbox|production`.
- Syntax verification with `compileall`.

### Changed

- Moved real client implementation to underscored importable module.
- Updated CLI to use the installable package instead of file-path import hacks.
- Updated Hebrew date display guidance to `DD/MM/YYYY`.
- Updated README installation instructions to `pip install -e .` and `pip install -r requirements-dev.txt`.
- Bumped metadata version to `2.1.0`.

### Removed

- Hyphenated client implementation file.

## [2.0.0] - 2026-06-02

### Added

- Comprehensive English guide.
- Comprehensive Hebrew guide with Israeli terminology, `₪`, and `DD-MM-YYYY` localization.
- API and regulation reference.
- End-to-end workflow guide.
- Troubleshooting guide.
- Test scenarios reference with more than 20 scenarios.
- Migration checklist.
- Typed synchronous and asynchronous client.
- Typer CLI.
- Pytest suite with more than 20 tests.
- Runnable examples.
- MIT license.
- Python project configuration and development requirements.

### Changed

- Reworked package into a neutral operational skill.
- Expanded metadata tags.
- Bumped version to `2.0.0`.

### Removed

- Branding.
- Visual marks and image references.
- Person or organization attribution metadata.
- Distribution callouts.

