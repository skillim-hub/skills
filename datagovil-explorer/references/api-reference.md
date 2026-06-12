# API and Regulatory Reference

## Base endpoint

`https://data.gov.il/api/3/action/{action}`

The portal follows CKAN action semantics. The installed client uses GET for public read actions. CKAN documentation also describes JSON POST requests for Action API calls, and data.gov.il documentation states that its CKAN API provides live access to the CKAN portion of the portal. Write actions, private resources, and restricted systems are outside this skill.

## Web-validated official references

Final validation was performed on 2026-06-02. Detailed snippets, pass-one sources, pass-two sources, and status tags are stored in `references/verification-log.md`.

## Israeli legal and regulatory considerations

This package does not provide legal advice. Use these references as operational guardrails when analyzing public data:

| Area | Israeli reference | Practical implication |
|---|---|---|
| Public access to government information | Freedom of Information Law, 5758-1998 | Prefer public, documented datasets and retain source metadata |
| Privacy and personal data | Protection of Privacy Law, 5741-1981 | Do not collect or republish unnecessary personal data |
| Data security duties | Privacy Protection Regulations (Data Security), 5777-2017 | Store exported data securely when it can identify people or businesses |
| Accessibility of digital public services | Equal Rights for Persons with Disabilities Regulations on service accessibility | Keep output readable and avoid image-only reporting |
| VAT and other statutory rates | Tax Authority and gov.il publications | Do not infer current tax rates from open-data exports; verify against the official tax source on the day of use |
| Consumer and business use | Consumer Protection Law, 5741-1981 and Business Licensing Law, 5728-1968 | Treat public records as supporting evidence, not as a final legal determination |

## Common response envelope

```json
{
  "help": "https://data.gov.il/api/3/action/help_show?name=package_search",
  "success": true,
  "result": {
    "count": 1,
    "results": []
  }
}
```

The client unwraps `result`. If `result` is a list, it returns `{"value": [...]}`.

## `package_search`

Search datasets.

```bash
curl -G "https://data.gov.il/api/3/action/package_search"   --data-urlencode "q=תחבורה ציבורית"   --data-urlencode "rows=5"   --data-urlencode "sort=metadata_modified desc"
```

```python
from datagovil_explorer import DatagovClient
client = DatagovClient()
result = client.package_search("תחבורה ציבורית", rows=5, sort="metadata_modified desc")
print(result["count"])
```

| Field | Meaning |
|---|---|
| `name` | Stable dataset identifier for `package_show` |
| `title` | Human-readable title |
| `organization` | Publishing body metadata |
| `metadata_modified` | Dataset metadata update timestamp |
| `resources` | Resource list, often summarized in search results |

## `package_show`

Inspect one dataset by id or name.

```bash
curl -G "https://data.gov.il/api/3/action/package_show"   --data-urlencode "id=DATASET_ID"
```

Response excerpt:

```json
{
  "success": true,
  "result": {
    "name": "DATASET_ID",
    "title": "Dataset title",
    "metadata_modified": "2026-06-02T10:00:00",
    "resources": [
      {
        "id": "RESOURCE_ID",
        "name": "Resource title",
        "format": "CSV",
        "datastore_active": true
      }
    ]
  }
}
```

## `resource_show`

Inspect one resource by id.

```bash
curl -G "https://data.gov.il/api/3/action/resource_show"   --data-urlencode "id=RESOURCE_ID"
```

Use it to confirm format, URL, update timestamp, and field metadata when available.

## `datastore_search`

Query a datastore-backed resource.

```bash
curl -G "https://data.gov.il/api/3/action/datastore_search"   --data-urlencode "resource_id=RESOURCE_ID"   --data-urlencode "limit=20"   --data-urlencode "offset=0"
```

With fields and filters:

```python
client.datastore_search(
    "RESOURCE_ID",
    limit=100,
    fields=["שם_ישוב", "סכום"],
    filters={"שם_ישוב": "חיפה"},
    sort="_id asc",
)
```

Response excerpt:

```json
{
  "success": true,
  "result": {
    "include_total": true,
    "limit": 20,
    "offset": 0,
    "records": [
      {"_id": 1, "שם_ישוב": "חיפה"}
    ],
    "total": 1000
  }
}
```

## `organization_list`

```bash
curl -G "https://data.gov.il/api/3/action/organization_list"   --data-urlencode "all_fields=true"
```

## `tag_list`

```bash
curl "https://data.gov.il/api/3/action/tag_list"
```

## Error table

| Condition | Typical signal | Recovery |
|---|---|---|
| Bad action or missing id | `success=false` with error payload | Check action name and required parameters |
| Dataset not found | HTTP 404 or CKAN not found error | Search again and copy `name` exactly |
| Resource not datastore-backed | Empty or failed `datastore_search` | Use `resource_show` and inspect file URL |
| Possible throttling or temporary blocking | HTTP 429 | Reduce request rate, retry with backoff; no fixed public quota was confirmed in the final validation pass |
| Temporary server failure | HTTP 500, 502, 503, 504 | Reduce page size and retry later |
| Invalid JSON | Decode error | Save raw body, retry, and report endpoint instability |
| Empty records | `records=[]` | Check filters, field names, resource id, and offset |
| Hebrew mismatch | Filters return no rows | Query a sample and copy exact Hebrew values |

## Request hygiene

Use bounded `limit` values. Store raw responses for audit. Avoid scraping HTML pages when an API action exists. Prefer official identifiers from CKAN responses over manually typed names. Do not document webhook event names for this package; the verified surface is request/response CKAN actions.
