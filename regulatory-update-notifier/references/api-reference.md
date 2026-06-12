# Israeli Source Reference

## Purpose

Use this reference to configure monitors for Israeli legal and regulatory sources. Treat endpoint examples as starting points. Confirm current endpoint behavior before production use because government pages and data services can change without notice.

Last web validation: 02/06/2026. See `references/verification-log.md` for the two-pass source audit.

## Source hierarchy

| Rank | Source type | Use for | Legal confidence |
|---:|---|---|---|
| 1 | Reshumot and official publication | Final laws, regulations, orders, commencement notices | Highest |
| 2 | Knesset official data and pages | Bills, readings, committee stages, legislative history | High for bill status |
| 3 | Ministry and authority pages | Guidance, procedures, circulars, enforcement notices, consultations | High for regulator position |
| 4 | Government Legislation Site consultations | Draft bills, draft secondary legislation, procedures, guidelines, comment deadlines | Draft only |
| 5 | Secondary reporting | Discovery and context | Not controlling |

## Validated source registry

| Source | URL | Format | Use | Validation note |
|---|---|---|---|---|
| Knesset OData v2 | `https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Bill` | OData | Bills and legislative metadata | Official Knesset OData manual and metadata confirm the service family and `KNS_Bill`; access may be blocked by geo controls. |
| Knesset site | `https://main.knesset.gov.il` | HTML/PDF/DOC | Committee, plenum, bill, and research material | Use as official legislative context. |
| Reshumot | `https://www.gov.il/he/departments/official_gazette` | HTML/PDF | Official Gazette publications | Use for binding publication confirmation. |
| Reshumot dynamic collector | `https://www.gov.il/he/departments/dynamiccollectors/gazette-official` | HTML/PDF | Searchable Official Gazette publications | Prefer when looking for a specific booklet or publication type. |
| Government Legislation Site | `https://www.tazkirim.gov.il/s/?language=iw` | HTML | Drafts and public comments | Use for public consultation deadlines and draft classification. |
| Israel Tax Authority | `https://www.gov.il/he/departments/israel_tax_authority` | HTML | VAT, bookkeeping, digital invoices, withholding tax | Use for tax authority guidance and services. |
| Consumer Protection and Fair Trade Authority | `https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority` | HTML | Consumer protection, distance selling, pricing, enforcement | Use for retail and ecommerce updates. |
| Privacy Protection Authority | `https://www.gov.il/he/departments/the_privacy_protection_authority` | HTML | Privacy, databases, information security, breach reporting | Use for privacy compliance updates. |
| Ministry of Labor | `https://www.gov.il/he/departments/labor` | HTML | Labor law, employment rights, permits, enforcement | Use for employer and worker-rights updates. |
| Ministry of Economy and Industry standards | `https://www.gov.il/he/departments/topics/standardization-import-reform` | HTML | Standards, import rules, product compliance | Use for importers, manufacturers, and product sellers. |

## Current validated rates and thresholds

| Topic | Current validated value | Effective date | Source handling |
|---|---:|---|---|
| Standard VAT rate on transactions in Israel and imports of goods | 18% | 01/01/2025 | Treat as current as of 02/06/2026. Recheck before issuing tax-critical instructions. |
| Israel Invoice allocation threshold for input-tax deduction | Above ₪10,000 before VAT | 01/01/2026 through 31/05/2026 | Monitor Tax Authority changes before using in production. |
| Israel Invoice allocation threshold for input-tax deduction | Above ₪5,000 before VAT | 01/06/2026 onward | Treat as current as of 02/06/2026. |

Do not hard-code thresholds into summaries unless the official source being summarized contains the threshold or the package verification log has confirmed it for the relevant date.

## Knesset legislative data

### Purpose

Track bills, readings, committee handling, and legislative status. Use bill data to identify potential future obligations. Do not mark a bill as binding without final enactment and official publication.

### Example request

```http
GET https://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Bill?$top=5&$orderby=LastUpdatedDate%20desc
Accept: application/json
```

### Example response shape

```json
{
  "value": [
    {
      "BillID": 123456,
      "Name": "Example bill title",
      "PublicationDate": "2026-06-02T00:00:00",
      "LastUpdatedDate": "2026-06-02T09:30:00",
      "KnessetNum": 25
    }
  ]
}
```

### Mapping

| Field | Internal field |
|---|---|
| `Name`, `BillName` | `title` |
| `PublicationDate`, `LastUpdatedDate` | `published_at` |
| `BillID` | id component |
| Knesset page URL | `url` |
| Stage or reading text | `status` support |

### Operational caveat

The Knesset OData endpoints can return maintenance or geo-block pages for some networks. Treat a 403, maintenance page, or non-OData HTML response as a source-availability issue, not as proof that no bill exists.

## Reshumot official gazette

### Purpose

Confirm final publication of statutes, regulations, notices, orders, and commencement provisions. Prefer this source when resolving whether a change is binding.

### Example discovery request

```http
GET https://www.gov.il/he/departments/official_gazette
Accept: text/html
```

### Expected response handling

HTML pages and linked documents often need extraction. Store the page URL, title, publication date, document link, and content hash.

### Mapping

| Signal | Internal classification |
|---|---|
| חוק, תקנות, צו, הודעה | `enacted` |
| תחילה ביום future date | `future-effective` |
| תיקון, הארכה, הוראת שעה | enacted with review note |
| PDF image only | manual extraction required |

## gov.il authority pages

### Purpose

Monitor regulator publications, guidance, procedures, enforcement notices, public-facing updates, and official service pages.

### Example request

```http
GET https://www.gov.il/he/departments/israel_tax_authority
Accept: text/html
```

### Common authorities

| Authority | Typical relevance | Suggested tags |
|---|---|---|
| רשות המסים בישראל | VAT, bookkeeping, digital invoices, withholding tax | tax, vat, invoices |
| הרשות להגנת הצרכן ולסחר הוגן | cancellation, disclosure, pricing, distance selling | consumer, ecommerce, retail |
| הרשות להגנת הפרטיות | databases, privacy notices, data security, breach duties | privacy, personal-data |
| משרד העבודה | wage, employment, labor inspections, permits | labor, employer |
| משרד הבריאות | clinics, pharmacies, food health rules | health |
| משרד הכלכלה והתעשייה | standards, imports, trade, consumer goods | import, standards |
| רשות שוק ההון | insurance, pensions, financial services | finance, insurance |

### Example HTML extraction

```json
{
  "title": "הנחיה בנושא ביטול עסקה",
  "published_at": "02/06/2026",
  "summary": "חובה להציג טופס ביטול עסקה באתר עד 30/06/2026",
  "url": "https://www.gov.il/example",
  "regulator": "Consumer Protection and Fair Trade Authority"
}
```

## Public consultations

### Purpose

Track drafts, memoranda, draft procedures, draft guidelines, and requests for comments. Extract comment deadline separately from effective date.

### Example source

```http
GET https://www.tazkirim.gov.il/s/?language=iw
Accept: text/html
```

### Example handling

```json
{
  "status": "draft-regulation",
  "response_deadline": "30/06/2026",
  "affected": ["ecommerce", "consumers"],
  "action": "Consider submitting comments before the deadline"
}
```

## Webhooks

No official webhook event names were confirmed for the monitored Israeli government sources in this package. Use polling, saved snapshots, content hashes, and explicit source URLs. Do not invent webhook names.

## Error table

| Error | Likely cause | Suggested handling |
|---|---|---|
| 400 | Unsupported query, changed parameter, malformed OData filter | Remove advanced filters and retry with a small top value |
| 403 | Bot control, blocked user agent, restricted endpoint | Use manual download or official export where available |
| 404 | Moved page or retired endpoint | Search the authority site and update the source registry |
| 429 | Rate limit | Back off, cache responses, avoid aggressive polling |
| 500 | Temporary service issue | Retry later and keep last known snapshot |
| TLS error | Certificate or network inspection issue | Validate network path and avoid disabling verification in production |
| Parse error | HTML layout or JSON shape changed | Save raw payload and update parser mapping |
| Empty result | No matching updates or source structure changed | Inspect raw response before concluding that no update exists |
| Geo-block or maintenance page | Official endpoint unavailable from the current network | Retry from an allowed network and preserve the failure page for audit |

## Request conventions

- Use a clear user agent.
- Prefer official language pages for the operational audience.
- Save raw content and extraction metadata.
- Limit polling frequency.
- Keep sandbox fixtures for tests and demonstrations.
- Do not scrape personal data from unrelated pages.

## Response normalization

Normalize every item to this shape:

```json
{
  "id": "stable-content-id",
  "source": "Official source name",
  "title": "Official title",
  "summary": "Short factual summary",
  "url": "https://official.example",
  "published_at": "02/06/2026",
  "regulator": "Authority name",
  "source_type": "html",
  "tags": ["consumer"],
  "industries": ["ecommerce"],
  "raw_text": "Extracted text for audit",
  "status": "guidance",
  "severity": "medium",
  "score": 55
}
```
