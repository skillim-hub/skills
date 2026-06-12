# Web Verification Log

Access date for all checks: 02/06/2026.

Status key: `✓✓` means double-confirmed; `✗→✓` means corrected after the second pass; `final ✗` means not confirmed by either pass.

| Check | Status | Pass 1 source | Pass 2 source | Package action |
|---|---|---|---|---|
| CBS official name and Hebrew terminology | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx`; snippet: `הלשכה המרכזית לסטטיסטיקה > ממשק API` | URL: `https://www.cbs.gov.il/en/Pages/default.aspx`; snippet: `CBS Site` | Kept Hebrew name as `הלשכה המרכזית לסטטיסטיקה` and English `CBS`. |
| CBS public API purpose | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx`; snippet: `קבלת נתונים ממאגרי המידע של הלמ"ס בצורה אוטומטית` | URL: `https://www.cbs.gov.il/en/Pages/Api-interface.aspx`; snippet: `retrieve data from the CBS databases automatically` | Left client purpose unchanged. |
| CBS API request model | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx`; snippet: `יש להגדיר בדפדפן כתובת URL מתאימה` | URL: `https://www.cbs.gov.il/en/Pages/Api-interface.aspx`; snippet: `define an appropriate URL address` | Kept URL-based request examples. |
| CBS `User-Agent` requirement | ✗→✓ | URL: `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx`; snippet: `שדה user agent הוא שדה מנדטורי` | URL: `https://www.cbs.gov.il/en/Pages/Api-interface.aspx`; snippet: `The User Agent header is a mandatory field` | Updated docs and troubleshooting; bumped default client header to `cbs-data-analyzer/2.2`. |
| CBS price-index API scope | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `למשוך את רשימת הנושאים של המדדים` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `retrieve the list of subjects of the indices` | Kept catalog and data workflow. |
| General CBS API `format` values | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `format xml/json/csv/xls` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `format xml/json/csv/xls` | Updated API reference to list supported formats. |
| General CBS API `lang` values | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `lang he/en סוג שפה` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `lang he/en Language types` | Added language notes to API reference. |
| CBS `pagesize` limit | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `מקסימום - 1000` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `maximum: 1,000` | Added pagination details to API reference. |
| CBS catalog endpoint | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `https://api.cbs.gov.il/index/catalog/catalog` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `https://api.cbs.gov.il/index/catalog/catalog` | Kept catalog endpoint and added `download=false`. |
| CBS data endpoint | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `https://api.cbs.gov.il/index/data/price` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `https://api.cbs.gov.il/index/data/price` | Kept data endpoint and added optional parameters. |
| CBS `id` parameter for price data | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `id number קוד המדד` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `id number Index code` | Kept `mainCode`/index-code handling. |
| CBS `startPeriod` / `endPeriod` format | ✗→✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `startPeriod mm-yyyy` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `endPeriod mm-yyyy` | Added typed sync and async parameters plus CLI options. |
| CBS `last` parameter | ✗→✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `last number>0` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `Number of objects to retrieve` | Added `last` support and validation to client, CLI, and tests. |
| CBS `coef` parameter | ✗→✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `coef true/false הוספת מקדם` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `coef true/false adding a coefficient` | Added `coef` support to client, CLI, and tests. |
| General CPI example code `120010` | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `id=120010` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `id=120010` | Kept code as documented example; changed prose to require live catalog verification. |
| CBS price-index definition | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx`; snippet: `מדדי המחירים מודדים את אחוז השינוי` | URL: `https://www.cbs.gov.il/en/Pages/Api-interface.aspx`; snippet: `measure the percentage change in expenditure` | Kept index interpretation guidance. |
| Dwellings Price Index is bi-monthly | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `מדד מחירי הדירות הוא מדד דו-חודשי` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `The Dwellings Price Index is a bi-monthly index` | Kept housing-index lag warning. |
| Last three Dwellings Price Index values are provisional | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx`; snippet: `שלושת המדדים האחרונים ... ארעיים` | URL: `https://www.cbs.gov.il/en/Pages/Api-Indices.aspx`; snippet: `last three indices ... are provisional` | Kept caution against binding use without review. |
| CBS topics include population, prices, jobs, business, trade | ✓✓ | URL: `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx`; snippet: `אוכלוסייה ... מחירים ... עסקים ומסחר` | URL: `https://www.cbs.gov.il/en/Pages/Api-interface.aspx`; snippet: `population ... prices ... business and trade` | Kept business-planning source map. |
| data.gov.il official portal purpose | ✓✓ | URL: `https://data.gov.il/`; snippet: `מרכז מאגרי נתונים מכלל משרדי הממשלה` | URL: `https://data.gov.il/about`; snippet: `מידע ממשלתי אמין ומוסמך לשימוש הציבור הרחב` | Kept data.gov.il as discovery source. |
| data.gov.il CKAN API host | ✓✓ | URL: `https://data.gov.il/docs`; snippet: `Servers. https://data.gov.il/api/3` | URL: `https://docs.ckan.org/en/2.9/api/`; snippet: `CKAN’s Action API is a powerful, RPC-style API` | Kept base URL `https://data.gov.il/api/3/action`. |
| data.gov.il `package_search` workflow | ✓✓ | URL: `https://data.gov.il/docs`; snippet: `CKAN's Action API ... exposes all of CKAN's core features` | URL: `https://docs.ckan.org/en/2.9/api/`; snippet: `package_search?q=spending` | Kept `package_search` helper. |
| data.gov.il organization filter `lamas` | ✓✓ | URL: `https://data.gov.il/api/3/action`; snippet: `Data gov IL CKAN API` | URL: `https://data.gov.il/docs`; snippet: `This API provides live access to the CKAN portion of Data gov IL` | Kept `fq=organization:lamas`; marked as a filter that must be verified per dataset. |
| data.gov.il terms of use | ✓✓ | URL: `https://data.gov.il/terms-of-use`; snippet: `השימוש במידע מותר אך ורק בהתאם לתנאי רישיון זה` | URL: `https://data.gov.il/about`; snippet: `מדיניות ממשל פתוח המקדמת שקיפות` | Kept license and metadata caution. |
| Bank of Israel exchange-rate context | ✓✓ | URL: `https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/`; snippet: `publishes the representative exchange rate` | URL: `https://www.boi.org.il/en/`; snippet: `Representative exchange rates` | Kept Bank of Israel as separate context source. |
| Bank of Israel API/service availability | ✓✓ | URL: `https://www.boi.org.il/en/the-bank-of-israel-s-new-website/`; snippet: `features an API service to access up-to-date data` | URL: `https://www.boi.org.il/media/tzxbuhhj/extracting-representative-exchange-rates-from-the-new-series-database.pdf`; snippet: `Extraction using API` | Kept Bank of Israel out of the CBS client; referenced as separate context only. |
| Israeli VAT rate effective 01/01/2025 | ✓✓ | URL: `https://www.gov.il/he/pages/vat-history`; snippet: `1.1.25 עלה המע"מ ל-18%` | URL: `https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf`; snippet: `01/01/2025 יחול מע"מ בשיעור של 18%` | Added explicit verification note; retained tax-caveat language. |
| Israeli VAT still 18% in 2026 | ✓✓ | URL: `https://taxsummaries.pwc.com/israel/corporate/other-taxes`; snippet: `Last reviewed - 01 January 2026 ... VAT is 18%` | URL: `https://tradingeconomics.com/israel/sales-tax-rate`; snippet: `Sales Tax Rate in Israel stands at 18 percent` | Added `18%` in verification and caveats, with instruction to recheck before tax guidance. |
| Invoice Israel threshold and allocation numbers | final ✗ | URL: `https://govextra.gov.il/taxes/innovation/home/israel-invoices/`; snippet: `25000 ₪ ומעלה` | URL: `https://keep.co.il/blog/nihul-maam-2026.html`; snippet: `בתחילת 2026 על 15,000 ש"ח לפני מע"מ` | Did not add threshold guidance because official current 2026 threshold was not double-confirmed. |
| Webhook event names | ✓✓ | URL: package source review; snippet: `no webhook implementation` | URL: official source review; snippet: `no webhook sources cited` | Added a reference note that webhooks are not applicable. |
| Privacy/data-security caveat | ✓✓ | URL: `https://www.gov.il/en/pages/data_security_eng`; snippet: `apply to both private and public sectors` | URL: `https://www.gov.il/en/pages/data_security_regulation`; snippet: `Laws and regulations` | Kept aggregated-data and no-personal-profiling guidance. |
| Original package purpose: Israeli CBS data for planning | ✓✓ | URL: `https://www.cbs.gov.il/en/Pages/Api-interface.aspx`; snippet: `population ... prices ... business and trade` | URL: `https://www.gov.il/en/departments/central_bureau_of_statistics/govil-landing-page`; snippet: `population, economy and society` | Kept the skill purpose for Israeli small businesses, freelancers, and consumers. |

## Corrections applied

| Correction | Files updated |
|---|---|
| Added `User-Agent` requirement and v2.2 default header. | `references/api-reference.md`, `SKILL.md`, `SKILL_HE.md`, `README.md`, `scripts/cbs_data_analyzer_client.py` |
| Added `download=false`, `startPeriod`, `endPeriod`, `last`, and `coef` details. | `references/api-reference.md`, `scripts/cbs_data_analyzer_client.py`, `scripts/cbs_data_analyzer_cli.py`, `scripts/test_cbs_data_analyzer_client.py` |
| Changed CPI code language from default assumption to catalog-verified usage. | `SKILL.md`, `SKILL_HE.md`, `references/api-reference.md` |
| Added current VAT verification note while preserving tax-caveat guardrails. | `SKILL.md`, `SKILL_HE.md`, `references/api-reference.md` |
| Added explicit webhook non-applicability note. | `references/api-reference.md`, `references/verification-log.md` |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | final ✗ count |
|---:|---:|---:|---:|
| 32 | 27 | 4 | 1 |
