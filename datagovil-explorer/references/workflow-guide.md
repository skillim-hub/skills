# Workflow Guide

## Workflow 1: Choose a retail location with public evidence

1. Search for transport, business licensing, municipal tax, parking, and demographic terms relevant to the city.
2. Save the search response for each term.
3. Inspect candidate datasets with `package_show`.
4. Select datastore-backed resources first, then CSV or XLSX resources.
5. Pull sample rows for the city or area name.
6. Normalize city names such as `תל אביב-יפו`, `תל אביב יפו`, and `תל אביב`.
7. Export the relevant rows to CSV.
8. Summarize operational impact: access, cost indicators, service proximity, and missing evidence.
9. State that final licensing, zoning, lease, and tax conclusions require professional verification.

```bash
datagovil-explorer search "רישוי עסקים תל אביב" --rows 5 --json-output > licensing-search.json
datagovil-explorer search "תחבורה ציבורית תל אביב" --rows 5 --json-output > transport-search.json
```

## Workflow 2: Prepare a freelancer proposal

1. Ask for geographic scope, date range, and decision need.
2. Search official datasets with Hebrew terms and ministry names.
3. Record counts and candidate dataset identifiers.
4. Inspect resources and field names.
5. Pull only a small sample until the schema is stable.
6. Estimate extraction effort based on datastore availability, pagination, field quality, and cleanup needs.
7. Include assumptions and exclusions in the proposal.

## Workflow 3: Consumer complaint evidence pack

1. Identify the public body and topic.
2. Search with consumer wording and official terminology.
3. Save dataset and resource metadata.
4. Query only the rows needed for the claim.
5. Export CSV or JSON with query parameters.
6. Summarize what the public data shows and what it does not show.
7. Attach source metadata and query parameters to the complaint.

## Workflow 4: Repeatable weekly export

1. Pin dataset id and resource id after inspection.
2. Store query fields, filters, sort order, and maximum records in configuration.
3. Run `datagovil-explorer export` with a fixed file name pattern.
4. Validate row count and column names after each run.
5. Keep raw JSON metadata from each run.
6. Compare update timestamps before replacing business dashboards.

```bash
datagovil-explorer export RESOURCE_ID --out exports/records-02-06-2026.csv --page-size 500 --max-records 5000
```

## Workflow 5: Validate schema before analysis

1. Run `resource_show` and save the fields list.
2. Query 5 rows and save a sample.
3. Compare current fields to the expected schema.
4. Stop if required fields are missing.
5. Continue only after documenting added, removed, and renamed fields.

## Workflow 6: Hebrew and spreadsheet handoff

1. Print JSON with `ensure_ascii=False`.
2. Export CSV with UTF-8 signature.
3. Use column names copied from the source unless a mapping table is included.
4. Format dates as DD/MM/YYYY and money as ₪.
5. Include limitations in the user's preferred language.
