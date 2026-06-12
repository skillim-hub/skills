# API and Regulation Reference

Use this reference to validate Israeli import-tax estimates against official sources. The skill does not depend on a confirmed public JSON API, webhook contract, or hidden endpoint. Use the official web services and regulatory pages below, record the access date, and keep the estimate marked as non-binding.

Access date used for this package version: 02/06/2026.

## Verified official and official-adjacent sources

| Area | Source | Verified use |
|---|---|---|
| VAT rate | Israel Tax Authority VAT history and tax glossary | Confirm VAT default of 18% from 01/01/2025 |
| Tariff classification | Tax Authority Customs and Purchase Tax Tariff service | Locate Israeli tariff code, duty, purchase tax, and conditions |
| Customs Book | Shaar Olami Customs Book | Browse tariff items, discounts, definitions, and item conditions |
| Personal import taxes | Tax Authority import tax calculator | Estimate taxes for personal import and check import-legality indicators |
| Personal import guide | Tax Authority and Ministry of Economy personal import guides | Check thresholds, taxable base, personal-use conditions, and documents |
| Customs exchange rate | Tax Authority customs glossary and personal-import guidance | Use official customs exchange-rate logic for filing checks |
| Import legality | Free Import Order and Ministry of Economy import legality topic | Identify required licenses, approvals, standards, and competent authorities |
| Mandatory standards | Ministry of Economy mandatory standards services | Check official standards and approval/exemption routes |
| Communications equipment | Ministry of Communications import-equipment pages | Check approval or exemption for landline/wireless communications equipment |
| Food | Ministry of Health National Food Services | Check importer registration, prior approval, and release requirements |
| Cosmetics | Ministry of Health cosmetics services | Check notification, parallel import, and applicable reform routes |
| Medical devices | Ministry of Health AMAR pages | Check medical-device registration/import review and authority routing |
| Vehicles and parts | Ministry of Transport and Ministry of Economy personal-import product pages | Check permits, lab approvals, and vehicle/part restrictions |
| Agriculture | Ministry of Agriculture import services | Check plant, animal, veterinary, phytosanitary, and quota requirements |
| Preferential origin | Customs glossary and trade-agreement texts | Check proof-of-origin rules before applying preferential rates |

## Verified web-service URLs

| Purpose | URL | Contract status |
|---|---|---|
| Customs and Purchase Tax Tariff service | `https://www.gov.il/he/service/customs-tariff` | Official service page |
| Customs Book entry page | `https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/he/CustomsBook/Import/CustomsTaarifEntry` | Official web interface, not a documented JSON API |
| Customs Book disclaimer | `https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/he/CustomsBook/Import/Doubt` | Official web page |
| Personal import tax calculator | `https://www.gov.il/he/service/customs-tax-calculation-import-by-israelis` | Official service page |
| Shaar Olami personal import calculator | `https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/PersonalImportTax` | Official web interface, not a documented JSON API |
| Ministry of Economy personal import search | `https://apps.economy.gov.il/Apps/PersonalImport/` | Official public search interface |
| Free Import Order digital text | `https://apps.economy.gov.il/Apps/FreeImport/decree` | Official public text interface |

## Endpoint and webhook validation result

No stable official public JSON endpoint or webhook event contract was confirmed for tariff lookup. Do not implement production automation against illustrative paths such as `/tariff/search` unless a current official technical contract is obtained directly from the competent authority.

Treat the `CustomspilotWeb` paths as browser-facing interfaces. They are useful for manual verification and source links, but their HTML shape and query behavior can change without notice.

## Recommended validation workflow

1. Normalize the tariff code by removing spaces, dots, and hyphens.
2. Open the Customs and Purchase Tax Tariff service or the Customs Book entry page.
3. Search by Israeli tariff code when known.
4. Search by Hebrew and English product terms when no code is known.
5. Review chapter, heading, subheading, suffix, and notes.
6. Extract duty rate, purchase tax rate, units, special formulas, and import conditions.
7. Check VAT rate from the Tax Authority VAT source.
8. Check customs exchange-rate logic for the filing date.
9. Check import legality in the Free Import Order and competent-authority pages.
10. Record source URLs, access date, and confidence level.
11. Mark the result as an estimate unless a binding ruling or customs entry exists.

## Response fields

| Field | Type | Description |
|---|---|---|
| `customs_value` | number | Goods + freight + insurance + valuation adjustments in ILS |
| `customs_duty` | number | Customs duty estimate |
| `purchase_tax` | number | Purchase tax estimate |
| `vat_base` | number | Amount on which VAT was calculated |
| `vat` | number | Import VAT estimate |
| `total_taxes` | number | Customs duty + purchase tax + VAT |
| `landed_cost` | number | Customs value + taxes + non-tax fees |
| `assumptions` | array | Rate, valuation, and treatment assumptions |
| `warnings` | array | Classification, regulatory, and documentation warnings |
| `source_refs` | array | Official sources checked and retrieval dates |

## Validation warnings

| Warning | Meaning | Required action |
|---|---|---|
| `NO_PUBLIC_API_CONTRACT` | No official JSON/API contract was verified | Use official web services manually or obtain a current contract |
| `TARIFF_NOT_BINDING` | Web tariff is an aid, not a legal ruling | Confirm against binding law or professional classification |
| `TEMPORARY_THRESHOLD_RISK` | Personal-import relief thresholds changed temporarily in 2026 | Verify the current rule on the estimate date |
| `SPECIAL_DUTY_FORMULA` | Duty is not a simple percentage | Collect units, weight, volume, alcohol content, or other required measures |
| `ORIGIN_PROOF_REQUIRED` | Preferential duty needs valid proof of origin | Request certificate/declaration before applying preferential rate |
| `REGULATED_GOODS` | Competent-authority approval may be required | Check ministry/service before shipping |
| `CUSTOMS_EXCHANGE_RATE_REQUIRED` | Filing calculation needs official customs exchange-rate logic | Do not rely only on card or marketplace FX rate |
| `MIXED_SHIPMENT` | Invoice contains multiple tariff classes | Split by line item |
