# API and Regulatory Reference

## Scope

Use this reference for official Israeli public-data workflows and legal/regulatory context relevant to information-only pension fund comparisons. Live endpoints, terminology, and regulation were web-validated on 2026-06-02; repeat validation before production use because public datasets and official websites can change.

## Source map

| Source | Use | Access pattern | Notes |
|---|---|---|---|
| Pensia Net public portal | Manual export and human verification | Browser export from official portal | Keep export date, selected filters, and original file. |
| Data.gov.il CKAN Action API | Machine retrieval of public datasets | `package_search`, `datastore_search`, `datastore_search_sql` | Resource IDs vary. Discover before fetching. |
| Capital Market, Insurance and Savings Authority | Regulatory and public-data context | Official publications and datasets | Treat as context, not personal advice. |
| Capital Market, Insurance and Savings Authority | Official pension-fund public-data context | Pensia Net and Data.gov.il resources | Store source URL and retrieval date. |


## Web-validated source baseline

| Item | Current verified baseline | Operational implication |
|---|---|---|
| Pensia Net | Official comparison system for Israeli pension funds. | Use for public return and fee comparisons. |
| Data.gov.il Pensia Net dataset | Published under `רשות שוק ההון, ביטוח וחיסכון`; resource IDs may change. | Discover package/resources before each production integration. |
| CKAN host | `https://data.gov.il/api/3/action/` | Use action endpoints; keep timeouts and explicit error handling. |
| Primary data endpoint | `datastore_search` | Use for ordinary resource reads. |
| SQL endpoint | `datastore_search_sql` | Use only with stable fields and sanitized, controlled queries. |
| VAT rate | 18% in 2026, verified separately. | Do not apply VAT to pension-return or management-fee calculations. |
| Licensed advice boundary | Pension advice and marketing are licensed activities. | Keep outputs information-only and avoid suitability recommendations. |

See `references/verification-log.md` for source URLs, snippets, and double-confirmation status.

## Data.gov.il CKAN Action API

### Package search

Use package search to discover current package and resource IDs.

```http
GET https://data.gov.il/api/3/action/package_search?q=%D7%A4%D7%A0%D7%A1%D7%99%D7%94-%D7%A0%D7%98
Accept: application/json
```

Typical response shape:

```json
{
  "success": true,
  "result": {
    "count": 1,
    "results": [
      {
        "name": "pensia-net",
        "title": "פנסיה-נט",
        "resources": [
          {
            "id": "DISCOVERED_RESOURCE_ID",
            "name": "Monthly public data",
            "format": "CSV",
            "url": "https://data.gov.il/.../resource/DISCOVERED_RESOURCE_ID/..."
          }
        ]
      }
    ]
  }
}
```

Validation:
- Confirm official publisher.
- Confirm resource title and fields match the intended dataset.
- Confirm format is machine-readable.
- Store package name, resource ID, and retrieval date.

### Datastore search

```http
GET https://data.gov.il/api/3/action/datastore_search?resource_id=DISCOVERED_RESOURCE_ID&limit=1000&offset=0
Accept: application/json
```

Typical response:

```json
{
  "success": true,
  "result": {
    "resource_id": "DISCOVERED_RESOURCE_ID",
    "fields": [
      {"id": "מספר קופה", "type": "text"},
      {"id": "שם קופה", "type": "text"},
      {"id": "תאריך דיווח", "type": "timestamp"},
      {"id": "תשואה חודשית", "type": "numeric"},
      {"id": "דמי ניהול מצבירה", "type": "numeric"}
    ],
    "records": [
      {
        "מספר קופה": "12345",
        "שם קופה": "קרן פנסיה לדוגמה",
        "תאריך דיווח": "2025-12-31",
        "תשואה חודשית": "0.82",
        "דמי ניהול מצבירה": "0.20"
      }
    ],
    "limit": 1000,
    "offset": 0,
    "total": 1
  }
}
```

Client behavior:
- Fetch pages until `offset + limit >= total`.
- Normalize rows after fetch.
- Preserve raw rows for audit.
- Raise an explicit error when `success` is false.
- Avoid high-volume polling.

### Datastore SQL

```http
GET https://data.gov.il/api/3/action/datastore_search_sql?sql=SELECT%20*%20FROM%20%22DISCOVERED_RESOURCE_ID%22%20LIMIT%20100
Accept: application/json
```

Use SQL only when the resource ID and field names are stable. Do not pass unsanitized user input into SQL strings.

## Manual export reference

When no current API resource is available:

1. Open the official Pensia Net portal.
2. Select fund type, reporting period, and population filters.
3. Export CSV or Excel.
4. Save the original file unchanged.
5. Normalize into JSON.
6. Store source URL, export date, selected filters, and checksum.

Metadata example:

```json
{
  "source_type": "manual_export",
  "source_name": "Pensia Net",
  "source_url": "https://pensyanet.cma.gov.il/",
  "exported_at": "02/06/2026",
  "filters": {
    "fund_type": "new pension funds",
    "period": "12-2025"
  },
  "file_name": "pensia-net-31/12/2025.csv"
}
```

## Error table

| Error | Meaning | User-facing response | Technical action |
|---|---|---|---|
| `SOURCE_NOT_OFFICIAL` | Marketing or unauthenticated source | Ask for official export or API resource | Reject as primary source |
| `RESOURCE_NOT_FOUND` | CKAN resource ID changed | State that the public resource changed | Run package search |
| `CKAN_SUCCESS_FALSE` | API returned failure | Show API error and stop | Inspect `error` object |
| `MISSING_REQUIRED_COLUMN` | Missing ID, name, or date | Request corrected source or mapping | Update alias table |
| `ENCODING_ERROR` | Hebrew decoding failed | Retry encoding | Try UTF-8-SIG, UTF-8, Windows-1255 |
| `PERCENT_PARSE_ERROR` | Percent values parse incorrectly | Verify source format | Inspect raw row |
| `PERIOD_MISMATCH` | Funds have different report dates | Avoid direct ranking | Align periods |
| `TRACK_MISMATCH` | Different target population or track | Split analysis or warn | Group by track |

## Regulatory context

| Source | Relevance | Safe use |
|---|---|---|
| Control of Financial Services (Provident Funds) Law, 5765-2005 | Supervision framework for pension/provident funds | Mention regulated-product context only |
| Control of Financial Services (Insurance) Law, 5741-1981 | Insurance and supervisory framework | Background only |
| Regulation of Financial Services (Pension Advice, Pension Marketing and Pension Clearing System) Law, 5765-2005 | Distinguishes licensed advice/marketing from general information | Explain why no personal recommendation is given |
| Extension Order for Mandatory Pension Insurance in Israel | Employer/payroll pension deposit context | Use for general context only |
| Capital Market Authority circulars and instructions | Reporting, product, and supervision rules | Verify current version before citing |

## Required source citation block

```text
Source: Pensia Net public data via Data.gov.il CKAN resource DISCOVERED_RESOURCE_ID
Retrieved: 02/06/2026
Reporting period: 31/12/2025
Limitations: Information only; not pension, investment, insurance, or tax advice.
```

## Client examples

Fetch CKAN:

```python
client = PensionFundTrackerClient()
records = client.fetch_ckan(resource_id="DISCOVERED_RESOURCE_ID", limit=1000)
```

Normalize local CSV:

```python
records = client.load_csv("pensia-net.csv")
issues = client.validate_records(records)
ranked = client.rank(records, metric="trailing_36m_return_pct")
```

Async load:

```python
async_client = AsyncPensionFundTrackerClient()
records = await async_client.load_csv("pensia-net.csv")
```

## Privacy and retention

- Keep official source files for reproducibility.
- Avoid storing identity numbers, medical details, family details, or salary data unless explicitly needed.
- Redact personal identifiers from examples.
- Use aggregate values for employer overviews.
