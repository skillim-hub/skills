# API and Regulation Reference

This reference lists official data interfaces, related public-data sources, and regulatory caveats used by the CBS Data Analyzer. Verify live endpoints and legal text before using results in a binding process. Current-source checks are recorded in `references/verification-log.md`.

## Official data sources

| Source | Use | Base URL | Verified detail | Notes |
|---|---|---|---|---|
| Israeli Central Bureau of Statistics | Statistical publications, tables, methodology | `https://www.cbs.gov.il` | Central official statistics source for population, economy, society, prices, labour, and many other subjects. | Primary public source for Israeli official statistics. |
| CBS API interface | Automated retrieval of CBS database content | `https://www.cbs.gov.il/he/Pages/ממשק-API.aspx` | CBS states that API data retrieval uses a URL template and that the `User-Agent` header is mandatory. | Always send a meaningful `User-Agent`. |
| CBS Price Indices API | CPI, housing price indices, producer prices, input-cost indices | `https://api.cbs.gov.il/index` | The API provides commands for index subjects and index data. | Use for index series when available. |
| CBS Price Indices catalog | Discover index codes | `https://api.cbs.gov.il/index/catalog/catalog?format=json&download=false` | The documented template is `/index/catalog/catalog`. | Returns chapters and `mainCode` values. |
| CBS Price Indices data endpoint | Fetch a time series | `https://api.cbs.gov.il/index/data/price?id=<mainCode>&format=json&download=false` | The documented template is `/index/data/price`; `id` is the index code. | General CPI is documented in examples with code `120010`; verify in the catalog before sensitive use. |
| data.gov.il CKAN API | Discover open government datasets | `https://data.gov.il/api/3/action` | Official docs describe live CKAN API access under `/api/3`. | Search with `fq=organization:lamas` for CBS datasets. |
| Bank of Israel | Interest and exchange-rate context when needed | `https://www.boi.org.il` | The Bank publishes representative exchange rates and monetary data separately from CBS. | Use only as context, not as a CBS statistic. |
| Israel Tax Authority | VAT and tax context when explicitly requested | `https://www.gov.il/he/departments/israel_tax_authority` | VAT history records the change to `18%` from `01/01/2025`; independent 2026 sources still show `18%`. | Do not infer tax treatment from CBS data. |
| Privacy Protection Authority | Privacy and data-protection guidance | `https://www.gov.il/he/departments/the_privacy_protection_authority` | Data-security regulations apply to private and public sectors. | Use aggregated public statistics; avoid personal profiling. |

## Regulation and compliance caveats

| Area | Citation target | Practical rule |
|---|---|---|
| Public data reuse | Israeli government open-data terms at data.gov.il and dataset-specific licenses | Read each dataset license and metadata before redistribution or commercial reuse. |
| Official statistics | CBS methodology pages and table notes | Cite table definitions, reference period, population universe, seasonality, and revisions. |
| Privacy | Protection of Privacy Law, 5741-1981, and Privacy Protection Regulations (Data Security), 5777-2017 | Use only aggregated data. Do not combine data in a way that identifies individuals. |
| Consumer and contract claims | Consumer Protection Law, 5741-1981, contract terms, and applicable court or authority guidance | Provide calculations only. Do not determine legality or enforceability. |
| VAT and taxation | VAT Law, Income Tax Ordinance, National Insurance rules, Tax Authority publications | As of the 2026 verification pass, the standard VAT rate is treated as `18%`; verify again before issuing tax guidance, invoices, or legal conclusions. |
| Housing and rent | The signed lease, relevant housing legislation, and official guidance | CPI indexation applies only if the agreement says so and the clause is enforceable. |
| Copyright | Copyright Law, 5768-2007, database terms, and open-data license terms | Cite sources and respect dataset terms. |

## CBS Price Indices API

### Required request practice

- Send `User-Agent`; CBS documents this header as mandatory.
- Send `format=json` for machine-readable client workflows.
- Send `download=false` when the response should be rendered as an API response instead of a physical file.
- Preserve the final request URL in reports.

### Catalog request

```bash
curl 'https://api.cbs.gov.il/index/catalog/catalog?format=json&download=false'   -H 'Accept: application/json'   -H 'User-Agent: cbs-data-analyzer/2.2'
```

### Catalog response shape

Actual fields may change. Code defensively.

```json
{
  "chapters": [
    {
      "mainCode": 120010,
      "chapterName": "Consumer Price Index - General",
      "chapterOrder": "..."
    },
    {
      "mainCode": 40010,
      "chapterName": "Apartment Prices",
      "chapterOrder": "..."
    }
  ]
}
```

### Price series request

```bash
curl 'https://api.cbs.gov.il/index/data/price?id=120010&format=json&download=false&last=6'   -H 'Accept: application/json'   -H 'User-Agent: cbs-data-analyzer/2.2'
```

### Price series response shape

The client accepts multiple variants. A typical response is shaped like this:

```json
{
  "month": [
    {
      "code": 120010,
      "name": "Consumer Price Index",
      "date": [
        {
          "year": 2026,
          "month": 4,
          "monthDesc": "April",
          "currBase": {"value": 106.4},
          "percent": 1.2,
          "percentYear": 1.9
        }
      ]
    }
  ]
}
```

Normalized point:

```json
{
  "period": "04-2026",
  "year": 2026,
  "month": 4,
  "value": 106.4,
  "monthly_change": 1.2,
  "annual_change": 1.9
}
```

### Documented price-index parameters

| Parameter | Endpoint | Required | Example | Notes |
|---|---|---:|---|---|
| `format` | catalog, data | Recommended | `json` | CBS supports `xml`, `json`, `csv`, and `xls` for general API parameters. |
| `download` | catalog, data | Recommended | `false` | Use `false` for normal API responses. |
| `lang` | catalog, data | No | `he`, `en` | Hebrew is the default in CBS documentation. |
| `page` | catalog, data | No | `1` | Current page for paginated responses. |
| `pagesize` | catalog, data | No | `100` | CBS documents a maximum of `1000`. |
| `id` | `/data/price` | Yes | `120010` | Use `mainCode` from catalog. |
| `startPeriod` | `/data/price` | No | `01-2025` | CBS documents `mm-yyyy`. |
| `endPeriod` | `/data/price` | No | `04-2026` | CBS documents `mm-yyyy`. |
| `last` | `/data/price` | No | `6` | Positive count of recent observations. |
| `coef` | `/data/price` | No | `true` | Adds chaining coefficients when supported. |

### Other CBS price-index endpoints to verify before use

| Endpoint | Purpose | Caution |
|---|---|---|
| `/index/catalog/tree` | Complete index-subject tree | Accepts `period`, `q`, and `string_match_type`; use when catalog chapters are too broad. |
| `/index/catalog/chapter` | Subjects by chapter | Requires a chapter code. |
| `/index/catalog/subject` | Codes by subject | Requires a subject identifier. |
| `/index/data/calculator/{id}` | CBS linkage calculator | Requires amount and dates; verify whether contract terms require a custom calculation instead. |
| `/index/data/price_selected` | Selected main indices by base | CBS English page notes XML-only support for this endpoint. |
| `/index/data/price_all` | All indices by bases | Large response; avoid using as a default path. |

## data.gov.il CKAN API

### Search request

```bash
curl 'https://data.gov.il/api/3/action/package_search?q=population&fq=organization:lamas&rows=10'   -H 'Accept: application/json'
```

### Search response shape

```json
{
  "success": true,
  "result": {
    "count": 2,
    "results": [
      {
        "id": "dataset-id",
        "name": "dataset-name",
        "title": "Population by locality",
        "organization": {"name": "lamas"},
        "metadata_modified": "2026-01-15T12:00:00"
      }
    ]
  }
}
```

### CKAN search parameters

| Parameter | Endpoint | Required | Example | Notes |
|---|---|---:|---|---|
| `q` | `package_search` | No | `population` | Query text; search Hebrew and English if needed. |
| `fq` | `package_search` | Recommended | `organization:lamas` | Filters to the CBS organization when present. |
| `rows` | `package_search` | No | `10` | Limit result count. |
| `start` | `package_search` | No | `0` | Pagination offset. |

## Webhooks

This package does not implement webhooks and does not cite webhook event names. If a future workflow adds a subscription or notification service, verify event names against that service's official documentation before adding examples.

## Error table

| HTTP/status symptom | Likely cause | Handling |
|---|---|---|
| `400 Bad Request` | Missing `id`, invalid parameter, malformed query | Validate parameters and show the source URL. |
| `401` or `403` | Network, firewall, missing required header, or access restriction | Confirm `User-Agent`, retry from another network, or use manual download from the portal. |
| `404 Not Found` | Wrong endpoint or obsolete `mainCode` | Fetch catalog and retry with a current code. |
| `429 Too Many Requests` | Rate limiting or proxy throttling | Back off and cache results. |
| `500` or `503` | CBS/data.gov maintenance | Retry later and provide manual verification path. |
| JSON decode error | HTML maintenance page or unexpected response | Inspect content type and body; request `format=json`. |
| Empty `month` list | Valid response with no data | Verify code, publication status, and table notes. |
| Missing `currBase.value` | Changed schema or incomplete period | Preserve raw record, skip invalid point, and warn. |
| Duplicate periods | Revised data or multiple bases | Keep raw records and prefer CBS-linked current-base values. |

## Retry and caching guidance

- Use a 20–30 second timeout for live calls.
- Cache catalog results for a workday.
- Cache price series by `mainCode` and retrieval date.
- Do not cache statutory rates, tax thresholds, or contract-sensitive current values without a freshness check.
- Save raw JSON for any report that may be audited.

## Response requirements

Every answer based on live or stored CBS data should include:

1. source name and endpoint;
2. retrieval date;
3. reference period;
4. series code or dataset identifier;
5. calculation formula;
6. assumptions and exclusions;
7. warning when the result affects a contract, payment, legal claim, tax report, investment decision, or consumer dispute.
