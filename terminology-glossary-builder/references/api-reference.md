# Reference: Israeli sources and interfaces

This skill is offline-first. It does not call external services automatically. Use the following sources for manual verification or for future integrations.

## Source registry

| Key | Authority | Scope | URL | Typical glossary terms |
|---|---|---|---|---|
| `govil` | Government of Israel | Central service and rights portal | `https://www.gov.il/` | rights pages, ministry landing pages, public guidance |
| `data_gov_il` | Government ICT Authority | Open data catalog interface | `https://data.gov.il/api/3/action/package_search` | registry discovery, public datasets |
| `tax_authority` | Israel Tax Authority | VAT, income tax, withholding, invoices, customs | `https://www.gov.il/he/departments/israel_tax_authority/govil-landing-page` | VAT, tax invoice, exempt dealer, import declaration |
| `btl` | National Insurance Institute | National Insurance and benefit obligations | `https://www.btl.gov.il/` | National Insurance contributions |
| `labor` | Ministry of Labor | Employment and labor guidance | `https://www.gov.il/he/departments/ministry_of_labor/govil-landing-page` | employment terms |
| `finance_ministry` | Ministry of Finance | Pension savings and economic guidance | `https://www.gov.il/he/departments/ministry_of_finance` | pension contributions, savings duties |
| `consumer_protection` | Consumer Protection and Fair Trade Authority | Consumer cancellation, warranties, fair trade | `https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority/govil-landing-page` | consumer cancellation, warranty certificate |
| `privacy` | Privacy Protection Authority | Privacy, databases, data protection guidance | `https://www.gov.il/he/departments/the_privacy_protection_authority/govil-landing-page` | privacy policy, database registration |
| `corporations` | Corporations Authority | Company records and corporate status | `https://www.gov.il/he/departments/corporations_authority/govil-landing-page` | company extract, private company |
| `standards` | Standards Institution of Israel | Standards and standard mark | `https://www.sii.org.il/` | standard mark, product standards |
| `boi` | Bank of Israel | Banking and monetary supervision | `https://www.boi.org.il/` | restricted account, interest rate |
| `isa` | Israel Securities Authority | Securities regulation and disclosure | `https://www.isa.gov.il/` | prospectus |
| `accessibility` | Commission for Equal Rights of Persons with Disabilities | Accessibility rules and public guidance | `https://www.gov.il/he/departments/commission_for_equal_rights_of_persons_with_disabilities/govil-landing-page` | accessibility statement |

## data.gov.il CKAN package search

Use this interface when a glossary needs to discover a relevant public dataset.

### Request

```http
GET https://data.gov.il/api/3/action/package_search?q=companies&rows=5
Accept: application/json
```

### Python request example

```python
import requests

response = requests.get(
    "https://data.gov.il/api/3/action/package_search",
    params={"q": "companies", "rows": 5},
    timeout=20,
)
response.raise_for_status()
print(response.json())
```

### Response shape

```json
{
  "help": "https://data.gov.il/api/3/action/help_show?name=package_search",
  "success": true,
  "result": {
    "count": 1,
    "results": [
      {
        "id": "dataset-id",
        "name": "dataset-name",
        "title": "Dataset title",
        "resources": []
      }
    ]
  }
}
```

### Error table

| Status or field | Meaning | Correction |
|---|---|---|
| `success: false` | CKAN action failed. | Read the returned error payload and adjust query parameters. |
| HTTP 400 | Invalid query parameter. | Remove unsupported filters or encode the query. |
| HTTP 429 | Rate limit or temporary throttling. | Retry later with backoff. |
| HTTP 5xx | Service issue. | Keep existing citations and schedule manual verification. |
| Empty `results` | No dataset matched. | Search Hebrew and English terms, then broaden the query. |

## GOV.IL and authority pages

Many Israeli authorities publish guidance as web pages rather than stable JSON interfaces. Treat these as authoritative pages, not machine-readable APIs.

### Verification request pattern

```http
GET https://www.gov.il/he/departments/israel_tax_authority/govil-landing-page
Accept: text/html
```

### Review response checklist

| Check | Required action |
|---|---|
| Authority name appears on the page. | Confirm the page belongs to the correct Israeli authority. |
| Date or update notice appears. | Record the date when using time-sensitive amounts or thresholds. |
| The page discusses the exact term. | Cite the page only for terms it actually supports. |
| The page is a search result or landing page only. | Continue to a more specific page before publication. |

## Tax Authority terms

Use Tax Authority sources for:

- מס ערך מוסף (מע"מ)
- חשבונית מס
- ניכוי מס במקור
- עוסק פטור
- עוסק מורשה
- מספר הקצאה לחשבונית
- רשימון יבוא when customs context applies

Avoid hard-coding rates and thresholds unless the checked page states the value and date. Attach DD/MM/YYYY to every date-sensitive amount.

## Consumer Protection terms

Use Consumer Protection and Fair Trade Authority sources for:

- ביטול עסקה צרכנית
- תעודת אחריות
- מחיר, דמי ביטול, אחריות ושירות לאחר מכירה

When exact cancellation windows matter, verify the product or service category. Do not reuse a deadline from another category.

## Privacy Protection terms

Use Privacy Protection Authority sources for:

- מדיניות פרטיות
- מאגר מידע
- רישום או הודעה על מאגר מידע
- אבטחת מידע where privacy context applies

Distinguish public glossary wording from operational privacy compliance instructions.

## Standards and import terms

Use Standards Institution of Israel and GOV.IL import guidance for:

- תו תקן
- תקן ישראלי
- חובות סימון
- בדיקות התאמה

Use Tax Authority customs resources for customs declarations and import taxation. Keep product safety, customs, VAT, and labeling terms separate.

## Local CLI response examples

### Create glossary request

```bash
tgb create "VAT" "Receipt" --industry tax --env sandbox --store ./glossaries.json
```

### Create glossary response

```json
{
  "id": "gls_7b4a2c6d9e10",
  "path": "glossaries.json",
  "entry_count": 2,
  "warnings": []
}
```

### Export request using the returned id

```bash
tgb export gls_7b4a2c6d9e10 --store ./glossaries.json --format json
```

### Export response shape

```json
{
  "id": "gls_7b4a2c6d9e10",
  "title": "English-Hebrew Terminology Glossary",
  "industry": "tax",
  "audience": "general",
  "language_mode": "bilingual",
  "environment": "sandbox",
  "source_registry_version": "2026-06-03",
  "created_at": "03/06/2026",
  "warnings": [],
  "entry_count": 2,
  "entries": []
}
```

## Local error table

| Error | Cause | Correction |
|---|---|---|
| `environment must be sandbox or production` | Invalid `--env` value. | Use `--env sandbox` or `--env production`. |
| `Glossary not found` | Export used an id that is not in the selected store. | Use the id from the create response and pass the same `--store`. |
| `max_terms must be positive` | Max term limit is zero or negative. | Use a positive integer or omit the option. |
| `Unknown source key` | Custom template references a missing source. | Add the source to the registry before using it. |
| `format must be markdown, json, or csv` | Unsupported output format. | Use one of the supported formats. |

## Web-validated facts for 2026

Use these facts only with the stated validity dates and recheck them before publication.

| Topic | Confirmed value | Validity or access date | Primary source |
|---|---|---|---|
| VAT standard rate | 18% | Effective 01/01/2025; checked 03/06/2026 | Tax Authority VAT glossary and VAT history |
| Exempt dealer ceiling | 122,833 ₪ | Tax year 2026; checked 03/06/2026 | Tax Authority exempt dealer service |
| Invoice allocation threshold | Above 10,000 ₪ from 01/01/2026; above 5,000 ₪ from 01/06/2026 | Checked 03/06/2026 | Tax Authority Israel Invoices services |
| Self-employed National Insurance total rates | 7.7% up to 7,703 ₪ and 18% above that up to 51,910 ₪ | Effective 01/01/2026; checked 03/06/2026 | National Insurance Institute |
| Self-employed pension duty | 4.45% first tier and 12.55% second tier | Checked 03/06/2026 | Ministry of Finance and corroborating rights guidance |
| Consumer cancellation fee cap | 5% or 100 ₪, whichever is lower, where the category allows a cancellation fee | Checked 03/06/2026 | Consumer Protection guidance and rights guidance |
| Privacy database duty wording | Use `database registration or notice`; do not assume registration applies to every database | Amendment 13 effective 14/08/2025; checked 03/06/2026 | Privacy Protection Authority |

## Webhook events

No webhook events apply to this package. The skill is offline-first and exposes only a local Python API and local CLI. The data.gov.il interface referenced here is CKAN REST-style access under `/api/3/action/...`, not an event subscription interface.

## Validation log

See `references/verification-log.md` for pass 1 and pass 2 source evidence, snippets, corrections, and summary counts.
