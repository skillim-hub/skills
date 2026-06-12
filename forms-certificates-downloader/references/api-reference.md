# API and Public Portal Reference

## Reference model

The downloader treats Israeli government sites as public document indexes, not as authenticated APIs. Many authorities publish forms through HTML pages, gov.il service pages, or authority-specific portals rather than stable JSON endpoints. Use this reference to decide whether a source is suitable for automated public discovery.

Read `references/verification-log.md` before changing official URLs. The current default registry was web-validated on 2026-06-02.

## Official public sources included

| Source name | Public portal | Typical use | Automation boundary |
|---|---|---|---|
| `tax-authority-gov-il` | `https://www.gov.il/he/departments/israel_tax_authority` | Tax Authority department pages, public tax topics, VAT notices, public certificates | Public discovery only |
| `tax-authority-public-forms` | `https://www.gov.il/he/departments/topics/income_tax_israel_tax_authority` | Income-tax services and public forms such as annual report forms | Public discovery only; use focused queries |
| `bituach-leumi-forms` | `https://www.btl.gov.il/טפסים%20ואישורים/forms/Pages/default.aspx` | National Insurance public form categories | Download or print public forms only |
| `bituach-leumi-certificates` | `https://www.btl.gov.il/טפסים%20ואישורים/אישורים/Pages/default.aspx` | National Insurance public certificate information | Personal certificate printing remains in official personal service |
| `gov-il-services` | `https://www.gov.il/he/services` | General service pages by ministry or topic | Use focused queries and small limits |
| `corporations-authority` | `https://www.gov.il/he/departments/israeli_corporations_authority` | Public corporation and nonprofit services and forms | Authenticated filings and paid file review remain manual |

## Web-validated regulatory notes

| Item | Current reference value | Practical use |
|---|---|---|
| VAT rate | 18% from 01/01/2025, double-checked during the 2026 validation pass | Mention only as context. Do not calculate filings or issue tax advice. |
| gov.il service counts | Dynamic and not suitable for hard-coding | Never assert a fixed number of services in code or documentation. |
| Bituach Leumi form search | The dedicated search page may be temporarily inactive | Prefer category pages and focused Hebrew queries. |
| Webhook event names | Not applicable | This package has no webhook receiver, subscription endpoint, or event schema. |

## Regulatory and operational boundaries

| Area | Practical rule |
|---|---|
| Privacy and data minimization | Do not store personal certificates in a shared public download directory. |
| Tax filings | Downloading a public form is not filing, reporting, or receiving tax advice. |
| National Insurance claims | Public form discovery is not submission and does not prove eligibility. |
| Electronic signatures | Signature and declaration steps must occur in official systems. |
| Terms of use | Respect public portal terms, robots guidance, rate limits, and authentication boundaries. |
| Accessibility and language | Preserve Hebrew titles and export CSV using UTF-8 with BOM for spreadsheet compatibility. |

## Request examples

### Discover public documents

```bash
forms-certificates-downloader discover tax-authority-public-forms \
  --query "1301" \
  --max-results 5 \
  --env production \
  --download-dir ./downloads \
  --json-output
```

Example response:

```json
[
  {
    "authority": "Israel Tax Authority",
    "title": "טופס 1301 לשנת 2026",
    "source_url": "https://www.gov.il/he/departments/topics/income_tax_israel_tax_authority",
    "document_url": "https://www.gov.il/BlobFolder/generalpage/forms/he/tofes-1301.pdf",
    "document_type": "pdf",
    "version_hint": "2026",
    "checksum_sha256": null,
    "fetched_at": null,
    "path": null,
    "size_bytes": null,
    "metadata": {
      "source_name": "tax-authority-public-forms",
      "tags": ["tax", "income-tax", "forms"],
      "env": "production"
    },
    "key": "israel-tax-authority::www.gov.il-BlobFolder-generalpage-forms-he-tofes-1301.pdf"
  }
]
```

### Create a saved request

```bash
forms-certificates-downloader create-request bituach-leumi-forms \
  --query "דמי לידה" \
  --limit 10 \
  --env production \
  --download-dir ./downloads \
  --json-output
```

Example response:

```json
{
  "created_at": "2026-06-02T09:15:00+00:00",
  "env": "production",
  "limit": 10,
  "query": "דמי לידה",
  "request_id": "0123456789abcdef0123456789abcdef",
  "source_name": "bituach-leumi-forms"
}
```

### Run a saved request

```bash
forms-certificates-downloader run-request 0123456789abcdef0123456789abcdef \
  --env production \
  --download-dir ./downloads \
  --json-output
```

Example response:

```json
{
  "changes": [
    {
      "current_checksum": "49f0e0d2f9a7b4b0c1d2e3f4567890abcdef1234567890abcdef1234567890",
      "current_path": "downloads/national-insurance-institute/תביעה-לדמי-לידה.pdf",
      "key": "national-insurance-institute::www.btl.gov.il-forms-maternity.pdf",
      "previous_checksum": null,
      "previous_path": null,
      "status": "added",
      "title": "תביעה לדמי לידה"
    }
  ],
  "downloaded": [
    {
      "authority": "National Insurance Institute",
      "title": "תביעה לדמי לידה",
      "document_type": "pdf",
      "checksum_sha256": "49f0e0d2f9a7b4b0c1d2e3f4567890abcdef1234567890abcdef1234567890",
      "fetched_at": "2026-06-02T09:16:00+00:00",
      "size_bytes": 174532,
      "path": "downloads/national-insurance-institute/תביעה-לדמי-לידה.pdf"
    }
  ],
  "env": "production",
  "query": "דמי לידה",
  "request_id": "0123456789abcdef0123456789abcdef",
  "source_name": "bituach-leumi-forms"
}
```

## Python client reference

### Constructor

```python
FormsCertificatesClient(
    download_dir="downloads",
    manifest_path=None,
    registry=None,
    timeout=30.0,
    user_agent="forms-certificates-downloader/2.2.0 public-document-client",
    fetcher=None,
    env="production",
)
```

| Parameter | Meaning |
|---|---|
| `download_dir` | Local folder for files, requests, and default manifest. |
| `manifest_path` | Optional explicit manifest path. |
| `registry` | Optional sequence of `PortalSource` objects. |
| `timeout` | Network timeout in seconds. |
| `user_agent` | HTTP user agent for public requests. |
| `fetcher` | Optional replacement fetcher for tests and offline fixtures. |
| `env` | `sandbox` or `production`. Affects metadata and example workflows. |

### Public methods

| Method | Use |
|---|---|
| `list_sources()` | Return configured sources. |
| `get_source(name)` | Return one source or raise `SourceNotFoundError`. |
| `discover(source_name, query, extensions, max_results)` | Parse a public source and return document records. |
| `download(record, filename)` | Save one document and compute checksum. |
| `track_records(records)` | Update manifest and return change statuses. |
| `refresh_source(source_name, query, max_results)` | Discover, download, and track one source. |
| `async_discover(...)` | Async wrapper for discovery. |
| `async_download(...)` | Async wrapper for one download. |
| `async_refresh_source(...)` | Async refresh workflow. |
| `refresh_all(query, max_results_per_source)` | Refresh all configured sources. |
| `find_manifest_records(query, authority)` | Search stored manifest records. |
| `export_manifest_csv(output_path)` | Export manifest records to CSV. |
| `create_download_request(source_name, query, limit, env)` | Save a request and return a request id. |
| `load_download_request(request_id)` | Load a saved request. |
| `run_download_request(request_id, track)` | Execute a saved request. |

## Error table

| Error | Typical cause | Corrective action |
|---|---|---|
| `SourceNotFoundError` | Source name is not in registry | Run `list-sources` or update registry. |
| `FetchError` | Network, unsupported scheme, HTTP failure, or timeout | Open URL manually, confirm public access, retry with a smaller source. |
| `ParseError` | Index page is not HTML or direct document | Use an HTML public index or direct file URL. |
| `RequestNotFoundError` | Saved request id missing or malformed | Recreate request and use the returned id. |
| `DownloaderError` | Tracking attempted before download | Download the record before `track_records`. |
| `ValueError` | Invalid environment or limit | Use `sandbox` or `production`; set positive limit. |

## Response status semantics

| Status | Meaning |
|---|---|
| `added` | The manifest did not contain the document key. |
| `updated` | The document key existed but SHA-256 changed. |
| `unchanged` | The document key existed and SHA-256 stayed the same. |

## Rate and safety guidance

Use a small limit, focused query, and official source pages. Do not run large unattended discovery against broad portals. Do not use this package for private areas or to bypass controls.
