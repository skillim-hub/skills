# API and Data Reference

This reference describes integration points commonly used for Israeli rocket-alert and public-shelter workflows. Endpoints, schemas, headers, and access rules can change. Validate all details against the official current source configured in production.

## Israeli sources and regulation categories

| Source / regulation category | Citation for implementation notes | Use in this skill |
|---|---|---|
| Home Front Command public alert feed | Home Front Command online alert services, commonly exposed through `/WarningMessages/alert/alerts.json` under `oref.org.il` | Current active alert areas |
| Home Front Command preparedness guidance | Home Front Command public guidance for protected spaces, alert behavior, and waiting instructions | Safety wording and protected-space hierarchy |
| Municipal emergency departments | Municipal shelter lists, emergency pages, GIS exports, and call centers | Public shelter location and opening notes |
| Israel Government Data Portal | `data.gov.il` datasets, including municipal/GIS datasets where available | Shelter datasets and locality reference data |
| Survey of Israel / GIS coordinate standards | WGS84 latitude/longitude for web and GeoJSON; Israel Grid only after conversion | Coordinate validation and distance calculation |
| Protection of Privacy Law, 5741-1981 | Israeli privacy obligations and related guidance | Location storage, logging, retention, redaction |
| Equal Rights for Persons with Disabilities Law, 5758-1998 and accessibility regulations | Accessibility obligations for service environments | Accessible route and assistance-buddy procedure |
| Civil Defense Law, 5711-1951 and related emergency-defense rules | Civil defense and protected-space context | Preparedness terminology and protected-space operations |
| Business Licensing Law, 5728-1968 and municipal licensing requirements | Requirements that may apply to customer-facing premises | Signage, crowd flow, and local compliance review |
| Labor safety obligations and workplace emergency procedures | Workplace safety and employer duties | Staff drills, training, and incident records |

For binding legal or regulatory decisions, check the official current text and obtain qualified professional advice. Do not infer legal compliance from a successful alert or shelter lookup.

## Active-alert endpoint

Common endpoint pattern:

```text
GET https://www.oref.org.il/WarningMessages/alert/alerts.json
```

Recommended headers:

```http
Accept: application/json, text/plain, */*
Accept-Language: he-IL,he;q=0.9,en;q=0.8
Referer: https://www.oref.org.il/
User-Agent: <descriptive application user agent>
Cache-Control: no-cache
```

Keep the URL configurable. Do not assume that endpoint policy, response shape, or rate limits remain unchanged.

### Response: no active alerts

```json
[]
```

or:

```json
{
  "id": "",
  "cat": "",
  "title": "",
  "data": []
}
```

Interpretation: no active alert is present only when the response is valid, fresh, and parsed successfully.

### Response: active alert

```json
{
  "id": "1700000000000",
  "cat": "1",
  "title": "ירי רקטות וטילים",
  "data": ["תל אביב - יפו", "רמת גן", "גבעתיים"]
}
```

Normalized output:

```json
[
  {
    "message_id": "1700000000000",
    "category": "1",
    "title": "ירי רקטות וטילים",
    "areas": ["תל אביב - יפו", "רמת גן", "גבעתיים"],
    "timestamp": "2026-06-04T12:00:00+03:00"
  }
]
```

### Response: callback wrapper

```javascript
callback({"id":"1700000000000","cat":"1","title":"ירי רקטות וטילים","data":["אשדוד"]})
```

The client extracts the JSON object between the outer parentheses and parses it as an alert payload.

## Error table

| HTTP status / error | Meaning | Required behavior |
|---|---|---|
| 200 valid empty payload | No active alert in payload | Return inactive status with freshness caveat |
| 200 malformed JSON | Schema, block page, encoding, or partial response | Raise parse error; do not report inactive |
| 204 | No content | Treat as unavailable unless configured source documents otherwise |
| 403 | Access blocked, headers missing, or endpoint policy | Back off; surface feed unavailable |
| 404 | Endpoint changed or misconfigured | Surface configuration error |
| 408 / timeout | Network or source latency | Retry with backoff; surface unavailable |
| 429 | Rate limit | Back off; reduce polling |
| 500 / 502 / 503 / 504 | Upstream failure | Retry with backoff; use fallback guidance |

## Polling guidance

- Use short-lived polling only for active user requests or an operational display.
- Keep a timeout shorter than the polling interval.
- Use exponential backoff for failures.
- Cache identical alert IDs briefly to prevent duplicate notifications.
- Stop background polling when no display, user, or escalation channel consumes the result.
- Log status, latency, payload size, alert count, and staleness.
- Do not log precise user location by default.

## Locality normalization

Normalize before matching:

1. Apply Unicode NFKC normalization.
2. Remove Hebrew niqqud.
3. Normalize geresh/gershayim variants.
4. Normalize hyphen variants to `" - "` for official names that use separated hyphens.
5. Collapse spaces.
6. Apply a verified alias table.

Example alias table:

```json
{
  "תא": "תל אביב - יפו",
  "תל אביב": "תל אביב - יפו",
  "tel aviv": "תל אביב - יפו",
  "jerusalem": "ירושלים",
  "haifa": "חיפה",
  "ashdod": "אשדוד"
}
```

Do not expand a regional council to all localities unless a verified, current mapping exists.

## Public-shelter datasets

Shelter sources vary by municipality. Prefer CSV, JSON, or GeoJSON with these fields:

| Field | Required | Notes |
|---|---:|---|
| name | Yes | Shelter name, number, or identifier |
| latitude | Yes | WGS84 decimal degrees |
| longitude | Yes | WGS84 decimal degrees |
| address | Recommended | Street, entrance, building, or landmark |
| city | Recommended | Municipality or locality |
| accessibility | Recommended | Use source wording; do not infer |
| opening_status | Optional | Mark as unverified unless source confirms |
| source_updated_at | Recommended | Use DD/MM/YYYY in Hebrew output |

### CSV example

```csv
name,address,city,latitude,longitude,accessibility
מקלט ציבורי 12,הרצל 10,תל אביב - יפו,32.073,34.780,לא ידוע
מקלט ציבורי 13,דיזנגוף 50,תל אביב - יפו,32.077,34.774,נגישות חלקית
```

### GeoJSON example

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [34.780, 32.073]},
      "properties": {
        "name": "מקלט ציבורי 12",
        "address": "הרצל 10",
        "city": "תל אביב - יפו"
      }
    }
  ]
}
```

GeoJSON coordinates are `[longitude, latitude]`.

## Request examples

Check alerts:

```bash
python scripts/red_alert_shelter_finder_cli.py alerts --area "חיפה"
```

Find nearest shelters:

```bash
python scripts/red_alert_shelter_finder_cli.py nearest \
  --lat 32.074 --lon 34.779 --shelters shelters.csv --limit 3
```

Generate business procedure:

```bash
python scripts/red_alert_shelter_finder_cli.py business-procedure \
  --city "אשדוד" --business-type "restaurant" --staff 8 --customers --deliveries
```

## Nearest-shelter response example

```json
[
  {
    "name": "מקלט ציבורי 12",
    "address": "הרצל 10",
    "city": "תל אביב - יפו",
    "latitude": 32.073,
    "longitude": 34.78,
    "distance_m": 145.0
  }
]
```

## Data-quality checks

- Verify every shelter has numeric WGS84 latitude and longitude.
- Reject latitude outside `29.0–34.0` and longitude outside `33.0–36.0` for Israel-focused deployments unless intentionally configured otherwise.
- Keep a source timestamp and source URL or file hash.
- Detect duplicate shelters within 10 meters and same name/address.
- Mark opening status as unverified unless the source provides reliable status.
- Record coordinate reference system before loading GIS exports.


## Web-validation corrections added in v3

- The Home Front Command official app and National Emergency Portal confirm official real-time/location-based alert channels.
- No official public documentation for the `alerts.json` endpoint path was confirmed. Keep the endpoint configurable and document it as observed/undocumented.
- Public shelter availability is municipal and dataset-dependent. Do not claim a complete nationwide shelter database unless the configured dataset proves coverage.
- VAT is not used by the client. If future business-cost examples add tax calculations, use 18% VAT for standard Israeli VAT unless a current official source changes it.
- No webhook event names are defined by this package.
