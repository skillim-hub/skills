# Changelog

All notable changes to this package are documented in this file.

The format is based on Keep a Changelog, and this package follows semantic versioning.

## [2.2.0] - 02/06/2026

### Added

- Web-validated `references/verification-log.md` with pass 1 and pass 2 source columns.
- Dated regulatory facts for VAT, annual fees, partnership annual fees, exempt-dealer threshold, online filings, privacy duties, consumer-law triggers, employment escalation, AML onboarding, and securities-offering escalation.
- `RegulatoryFact`, `get_regulatory_facts()`, and `regulatory_facts_payload()` in the Python client.
- CLI `facts` command.

### Verified findings

-  VAT standard rate is 18% from 01/01/2025 and remains current in 2026 — Added current 18% VAT fact to guides, reference, and client facts.
-  Knesset approval confirms VAT increase effective 01/01/2025 — Kept date in DD/MM/YYYY form and added source note.
-  2026 company annual fee: reduced ₪1,338 until 31/03/2026; regular ₪1,777 from 01/04/2026 — Added 2026 annual-fee values and a verification warning.
-  2026 partnership annual fee: reduced ₪1,333 until 31/03/2026; regular ₪1,771 from 01/04/2026 — Added partnership fee values to reference facts.
-  Private company annual report updates address, shareholders, directors, authorized reporters, and branches — Kept workflow; added online-only and field list to verification reference.
-  Company filings are generally online through Corporations Online from 27/06/2024 — Strengthened online-filing instructions.
-  Annual report access uses national identification or smart card — Added authentication note.
-  Company annual fee is owed once each calendar year unless exempt for registration year or dissolved/erased — Kept annual fee workflow; added exact 2026 values.
-  Dormant/no-activity companies still owe annual report and fee while registered — Strengthened dormant-company troubleshooting.
-  Companies may be marked violating law for missing annual report or annual fee — Added sanction-specific troubleshooting details.
-  Company share reports cover transfer, allotment, registered-capital changes, and issued-capital reductions — Kept transfer workflow; added official Form 3 reference.
-  Director-change service reports changes in board composition — Kept director workflow; added Form 6 reference.
-  Company names can be refused for similarity, misleading name, public-policy issue, mixed Hebrew/English, or trademark conflict — Kept naming anti-patterns; added official rejection list.
-  Company extract/basic public information may be free but can be incomplete; company file is paid — Added extract caveat to due-diligence workflow.
-  Corporations Authority handles Registrar of Companies, Partnerships, Amutot, and other registers — Kept terminology: Corporations Authority / רשות התאגידים.
-  Non-profit alternatives include amuta and public-benefit company registration — Kept entity-choice decision tree.
-  Partnership alternative is handled by Registrar of Partnerships under the Partnerships Ordinance — Kept partnership branch in decision tree.
-  Exempt dealer 2026 turnover threshold is ₪122,833 and some professions still require licensed dealer registration — Added 2026 threshold to reference and client facts.
-  Private company/tax registration is separate; Form 4436 covers corporate income tax and withholding files — Kept warning that corporate registration is not tax registration.
-  Privacy database registration duties changed under Amendment 13; general registration duty narrowed — Updated privacy escalation wording from broad registration warning to Amendment 13-specific warning.
-  Sensitive personal-data database notification duty can apply above 100,000 data subjects — Added privacy threshold to troubleshooting and references.
-  Consumer cancellation rights can include 14-day cancellation windows for distance/Internet transactions — Added consumer-law reminder for online sellers.
-  Employment law compliance is independent of company formation — Kept employment escalation trigger.
-  Bank onboarding may require beneficial-owner and controlling-person declarations under AML rules — Kept bank onboarding and beneficial-ownership checklist.
-  Securities offerings to the public require prospectus analysis and legal escalation — Kept securities/fundraising escalation trigger.
-  No public API host, endpoint path, or webhook event names apply to this non-API skill — Added explicit non-API/webhook statement to api-reference.

### Changed

- Updated annual-report workflows to mention the 2026 company annual-fee amounts with a re-verification warning.
- Updated Hebrew and English guides with a dated 2026 regulatory-facts section.
- Updated references to state explicitly that this is a non-API skill with no webhook events or endpoint paths.

## [2.1.0] - 02-06-2026

### Added

- Neutrality, authorship-field, visual-asset-link, and emoji audit report.
- Hebrew quality-assurance log.
- Installable `corporate_law_guide` Python package.
- Case creation workflow that returns `case_id` for chained CLI steps.
- `pytest-asyncio` development dependency.
- Environment-aware examples that accept `--env sandbox|production` and read environment variables.

### Changed

- Replaced the hyphenated client filename with `scripts/corporate_law_guide_client.py`.
- Updated imports to use the installable package.
- Updated README installation to use `pip install -e .` and `pip install -r requirements-dev.txt`.
- Updated Israeli date localization to `DD/MM/YYYY`.
- Improved Hebrew terminology and reduced unnecessary English terminology.

### Removed

- Hyphenated client module.
- Public Markdown emoji and visual-asset references.

## [2.0.0] - 02-06-2026

### Added

- Comprehensive English operational guide.
- Comprehensive Hebrew operational guide with Israeli terminology.
- Regulatory and workflow reference.
- End-to-end workflow guide.
- Troubleshooting guide.
- Test-scenarios reference with 30 scenarios.
- Migration checklist.
- Typed sync and async Python helper client.
- Full CLI with Typer support and argparse fallback.
- Pytest suite with more than 20 tests.
- Runnable example scripts.
- README, MIT license, pyproject configuration, and development requirements.

### Changed

- Reworked package into neutral voice.
- Expanded coverage for Israeli small businesses, freelancers, consumers, founders, directors, and shareholders.
- Localized dates and currency formatting.

### Removed

- Branding callouts.
- Image references.
- Creator/contributor metadata.
- Promotional or distribution callouts.
