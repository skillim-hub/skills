# Web Verification Log

Access date for all rows: 2026-06-02. Snippets are short excerpts from search results or opened sources and stay under 140 characters. Pass 2 used a different query or source where possible.

| Check | Status | Pass 1 source | Pass 1 snippet | Pass 2 source | Pass 2 snippet | Package action |
|---|---|---|---|---|---|---|
| data.gov.il portal purpose | ✓✓ | https://data.gov.il/ | "אתר מאגרי המידע הממשלתיים מרכז מאגרי נתונים" | https://data.gov.il/about | "data.gov.il המבוסס פלטפורמת Ckan" | Kept purpose as public government dataset discovery and analysis |
| Official CKAN API documentation host | ✓✓ | https://data.gov.il/docs | "Data Gov CKAN API Documentation 1.0.0. OAS 3.0" | https://data.gov.il/docs | "This API provides live access to the CKAN portion of Data gov IL" | Kept `https://data.gov.il/api/3` as production base URL |
| CKAN action path `package_search` | ✓✓ | https://data.gov.il/docs | "GET. /action/package_search. Find packages" | https://docs.ckan.org/en/2.9/api/ | "package_search?q=spending" | Kept search command and client method |
| CKAN action path `package_show` | ✓✓ | https://data.gov.il/docs | "/action/package_show. Get metadata" | https://docs.ckan.org/en/2.9/api/ | "Return the metadata of a dataset" | Kept dataset inspection method |
| CKAN action path `resource_show` | ✓✓ | https://data.gov.il/docs | "/action/resource_show. Get metadata" | https://docs.ckan.org/en/2.9/api/ | "Return the metadata of a resource" | Kept resource inspection method |
| CKAN action path `datastore_search` | ✓✓ | https://data.gov.il/api/1/util/snippet/api_info.html?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3 | "https://data.gov.il/api/3/action/datastore_search" | https://docs.ckan.org/en/2.9/maintaining/datastore.html | "The DataStore API: search, filter and update the data" | Kept datastore query method |
| CKAN action path `organization_list` | ✓✓ | https://data.gov.il/api/3/action/organization_list | "success": true | https://docs.ckan.org/en/2.9/api/ | "Get JSON-formatted lists of a site's datasets, groups or other CKAN objects" | Kept organization list helper |
| CKAN `package` terminology means dataset | ✓✓ | https://docs.ckan.org/en/2.9/api/ | "Package has exactly the same meaning as dataset" | https://data.gov.il/docs | "package_search" appears as dataset search in docs | Kept docs explaining package/dataset naming |
| CKAN response envelope `success=false` + `error` | ✓✓ | https://docs.ckan.org/en/2.9/api/ | "success": false and an "error" key | https://data.gov.il/api/3/action/organization_list | "success": true | Kept API error handling and tests |
| GET requests for read actions | ✓✓ | https://docs.ckan.org/en/2.9/api/ | "GET-able API functions" | https://data.gov.il/docs | "GET. /action/package_search" | Kept GET-based client and clarified POST support in reference |
| Public `organization_list` read without token | ✓✓ | https://data.gov.il/api/3/action/organization_list | "success": true | https://data.gov.il/docs | "GET. /action/package_search" | Kept public-read client behavior but avoided documenting a formal no-key policy |
| Official fixed rate limit or quota | final ✗ | https://data.gov.il/docs | No fixed quota found | https://docs.ckan.org/en/2.9/api/ | No data.gov.il quota found | Reworded 429 as defensive handling, not an official quota |
| Webhook event names | final ✗ | https://data.gov.il/docs | No webhook surface found | https://docs.ckan.org/en/2.9/api/ | Request/response Action API documented | Marked webhooks as not applicable for this package |
| Current Israeli VAT rate from 01/01/2025 | ✓✓ | https://www.gov.il/he/pages/vat-history | "1.1.25 עלה המע"מ ל-18%" | https://fs.knesset.gov.il/globaldocs/MMM/fdf809b1-c6bf-f011-a865-005056aa9911/2_fdf809b1-c6bf-f011-a865-005056aa9911_11_21444.pdf | "בישראל שיעור המע"מ הוא 18%" | Added reminder to verify statutory rates outside CKAN before use |
| VAT 18% still reflected in 2026 materials | ✓✓ | https://fs.knesset.gov.il/globaldocs/MMM/fdf809b1-c6bf-f011-a865-005056aa9911/2_fdf809b1-c6bf-f011-a865-005056aa9911_11_21444.pdf | "accessed: January 18th 2026" | https://www.gov.il/BlobFolder/reports/budget-plan-multi-years/he/budget-plan-multi-years_budgetplanupdate_2026-2028_publish-062025.pdf | "העלאת שיעור המע"מ מ-17% ל-18%" | No calculator added; skill remains data.gov.il focused |
| Invoice allocation threshold 2026 | ✓✓ | https://www.gov.il/he/pages/pa301225-2 | "החל מיום 1.1.2026 יידרש מספר הקצאה ייחודי" | https://www.gov.il/he/pages/pa240525-1 | "מ-5,000 ₪" | Kept outside scope; documented that current thresholds require official verification |
| Freedom of Information Law name and date | ✓✓ | https://main.knesset.gov.il/Activity/Legislation/Laws/pages/lawprimary.aspx?lawitemid=2000657 | "חוק חופש המידע, התשנ"ח-1998" | https://www.gov.il/he/pages/cpfta_hofesh_hamida | "נחקק ב-19 במאי 1998" | Kept legal guardrail reference |
| Protection of Privacy Law name and date | ✓✓ | https://fs.knesset.gov.il/9/law/9_lsr_208332.PDF | "חוק הגנת הפרטיות, התשמ"א1981" | https://www.gov.il/he/pages/rishom_tikon13 | "חוק הגנת הפרטיות, התשמ"א -1981" | Kept privacy guardrail and personal-data caution |
| Open-data publication policy | ✓✓ | https://www.gov.il/he/pages/2016_dec1933 | "הנגשת מאגרי מידע ממשלתיים לציבור" | https://library.mevaker.gov.il/sites/DigitalLibrary/Documents/2021/71C/2021-71c-102-Maagarey-Meyda.pdf | "פלטפורמה לפרסום כלל מאגרי המידע" | Kept open-government framing |
| Hebrew official terminology for portal | ✓✓ | https://data.gov.il/ | "מאגרי המידע הממשלתיים" | https://data.gov.il/about | "מאגרי המידע הממשלתיים - data.gov.il" | Kept Hebrew terminology and avoided unnecessary transliteration |
| Sandbox endpoint | ✗→✓ | Package v2 implied a selectable sandbox | No official sandbox host found | https://data.gov.il/docs | Production docs list data.gov.il API, not a sandbox | Clarified sandbox is user-provided test endpoint only |
| Public Markdown decorative assets | ✓✓ | Local grep audit | No decorative asset references found after v2 audit | Local grep audit after v3 edits | No decorative asset references found | Preserved neutral public Markdown |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | Final ✗ count |
|---:|---:|---:|---:|
| 22 | 19 | 1 | 2 |

Final ✗ rows are intentionally treated as unconfirmed, not as supported product behavior. Do not document a fixed quota or webhook event list without a future official source.
