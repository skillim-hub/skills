# Changelog

All notable changes to this package are documented in this file.

The format follows Keep a Changelog principles, and this package uses semantic versioning.

## [2.2.0] - 02/06/2026

### Added

- Two-pass web validation log with source URLs, snippets, access dates, and correction statuses.
- Official-source warning for live personal-import thresholds and customs exchange-rate handling.
- Web-validated workflow for checking rates, thresholds, tariff-code pages, and import-legality sources.

### Changed

- Rewrote the API reference to remove unverified illustrative endpoint paths.
- Marked Shaar Olami and Tax Authority tariff tools as official web interfaces, not confirmed public JSON APIs.
- Kept VAT default at 18% after double-confirming official sources.
- Treated personal-import thresholds as live rules after pass-2 correction of temporary 2026 relief information.

### Verification findings

-  `VAT-18`: Israeli VAT is 18% from 01/01/2025 and remains the configured 2026 default. Action: Kept default VAT at 0.18 and added live-source verification notes.
-  `IMPORT-TAXES`: Import taxes include customs duty, purchase tax, and VAT. Action: Kept terminology and aligned guide wording.
-  `TARIFF-BOOK`: The Customs and Purchase Tax Tariff is the key official tool for tariff classification and rates. Action: Kept tariff-code workflow and added caution that the web tariff is an aid, not legislation.
-  `TARIFF-NOT-BINDING`: Online tariff pages are preliminary aids and do not replace legislation or professional classification. Action: Strengthened disclaimer language in guides and API reference.
-  `PERSONAL-CALCULATOR`: The Tax Authority provides a personal-import tax calculator that can also surface import-legality requirements. Action: Added calculator as live validation step, not as a hidden API dependency.
- → `PERSONAL-THRESHOLD`: Personal-import tax thresholds are live rules; the baseline guide shows $75 and the 2026 $130 relief was temporary/rejected for continuation. Action: Corrected docs to avoid hard-coding temporary 2026 thresholds; added live-rule warning.
-  `SHIPPING-INSURANCE`: Taxable amount calculations can include shipping and insurance; relief-threshold checks may treat separated shipping differently. Action: Clarified CIF and threshold handling separately.
-  `CUSTOMS-EXCHANGE`: Customs exchange-rate handling is not the same as an arbitrary market rate. Action: Added warning to use official customs exchange rate for filing; helper still accepts user-supplied rate.
-  `FREE-IMPORT-ORDER`: Import legality and approvals are governed through the Free Import Order and related competent authorities. Action: Kept import-legality decision point and added source list.
-  `MANDATORY-STANDARDS`: Goods subject to official standards can require standards approval, exemption, or group-based import handling. Action: Kept standards-warning workflow and cited official lookup.
-  `COMMUNICATIONS`: Landline/wireless communications equipment may require Ministry of Communications customs-release approval or exemption. Action: Kept wireless warning, avoiding blanket claims that all wireless devices require approval.
-  `FOOD`: Food imports can require Ministry of Health National Food Services registration/approval. Action: Strengthened food/supplement warning.
-  `COSMETICS`: Cosmetic imports use Ministry of Health notification/parallel import tracks and requirements. Action: Kept cosmetic warning and noted live regulatory review.
-  `MEDICAL-DEVICES`: Medical devices may require AMAR/Ministry of Health import review, and tariff classification affects the competent authority. Action: Kept medical-device warning and separated classification from health approval.
-  `VEHICLE-PARTS`: Vehicle and vehicle-part imports can require Ministry of Transport or lab approval. Action: Kept vehicle/parts warning; avoided using one product-page quantity as a universal rule.
-  `AGRICULTURE`: Agricultural/plant/animal imports may require Ministry of Agriculture services, permits, quotas, or certificates. Action: Kept agriculture warning.
-  `PREFERENTIAL-ORIGIN`: Preferential customs treatment depends on trade agreement rules and proof of origin. Action: Kept origin proof warning and added dual-scenario workflow.
-  `CIF-VALUATION`: CIF/transaction value commonly includes goods value, freight, and insurance for customs-value estimation. Action: Kept CIF formula, with exceptions and documentation caveats.
- → `PUBLIC-API`: No stable official public JSON API or webhook contract was confirmed for tariff lookup; official sources are web services/pages. Action: Removed pseudo-API examples and documented official web-service URLs as non-contractual.
-  `WEBHOOKS`: Webhook event names are not applicable to this non-webhook skill package. Action: Documented non-applicability; no code changes needed.

## [2.1.0] - 02-06-2026

### Added

- Branding and visual-asset audit report.
- Hebrew quality-assurance log.
- Installable package module with direct imports.
- Stored estimate workflow with `create` and `show` commands.
- Example scripts that read environment variables and accept sandbox or production mode.
- `pytest-asyncio` development dependency.

### Changed

- Moved the client implementation to package code and underscored compatibility import.
- Removed the hyphenated client file.
- Updated quick-start commands to chain a created estimate identifier into the next command.
- Localized Hebrew date guidance to DD/MM/YYYY.
- Strengthened public Markdown neutrality checks.

## [2.0.0] - 02-06-2026

### Added

- Comprehensive English guide with decision trees, examples, edge cases, troubleshooting, anti-patterns, and production checklist.
- Full Hebrew guide with Israeli terminology, ₪ formatting, and DD-MM-YYYY localization.
- API and regulation reference for Israeli tariff, VAT, purchase tax, customs valuation, and import-approval checks.
- End-to-end workflow guide for consumers, businesses, purchase tax review, origin claims, repairs, mixed shipments, broker handoff, and accounting handoff.
- Troubleshooting guide.
- Test scenarios reference with 30 concrete scenarios.
- Migration checklist.
- Typed calculation client with synchronous and asynchronous methods.
- Typer CLI for estimates and scenario templates.
- Pytest suite with more than 20 tests.
- Runnable examples for consumer, business, purchase tax, repair, mixed shipment, and JSON input scenarios.
- Python packaging files and development requirements.

### Changed

- Reworked content into a neutral, imperative operating style.
- Made VAT configurable instead of treating a default as permanent.
- Split government taxes from courier and broker service fees.
- Expanded warnings for regulated goods, uncertain classification, and incomplete valuation.

### Removed

- Branding, visual marks, decorative marks, image references, author metadata, and distribution callouts.
