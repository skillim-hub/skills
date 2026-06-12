# Test Scenarios

Use these scenarios to validate the client, CLI, examples, and analytical guidance. None require private credentials.

| Number | Scenario | Expected result |
|---:|---|---|
| 1 | Scenario 1: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 2 | Scenario 2: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 3 | Scenario 3: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 4 | Scenario 4: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 5 | Scenario 5: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 6 | Scenario 6: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 7 | Scenario 7: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 8 | Scenario 8: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 9 | Scenario 9: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 10 | Scenario 10: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 11 | Scenario 11: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 12 | Scenario 12: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 13 | Scenario 13: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 14 | Scenario 14: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 15 | Scenario 15: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 16 | Scenario 16: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 17 | Scenario 17: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 18 | Scenario 18: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 19 | Scenario 19: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 20 | Scenario 20: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 21 | Scenario 21: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 22 | Scenario 22: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 23 | Scenario 23: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 24 | Scenario 24: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 25 | Scenario 25: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 26 | Scenario 26: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 27 | Scenario 27: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 28 | Scenario 28: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 29 | Scenario 29: validate client or workflow behavior | Expected deterministic result or clear diagnostic |
| 30 | Scenario 30: validate client or workflow behavior | Expected deterministic result or clear diagnostic |

## Concrete scenarios

- Search with Hebrew query `תחבורה ציבורית`; verify URL encoding and unwrapped result.
- Search with English query `transport`; verify query parameter.
- Search with `rows=0`; inspect count without records.
- Search with organization filter; verify `fq` encoding.
- Call `package_show` using dataset `name`.
- Call `resource_show` using resource `id`.
- Query datastore resource with no filters.
- Query datastore with exact Hebrew filter.
- Query datastore with selected fields.
- Page through records with `offset`.
- Export CSV with Hebrew fields.
- Retry temporary connection error.
- Handle HTTP 404.
- Handle CKAN `success=false`.
- Handle invalid JSON body.
- List organizations and tags.
- Format `2026-06-02` as `02/06/2026`.
- Format `12345.5` as `₪12,345.50`.
- Extract first dataset id from search response.
- Extract first resource id from dataset response.
- Use `--env sandbox` with configured environment variable.
- Run CLI `first-dataset-id` and chain into `dataset`.
- Run an example script with `--env production`.
- Run `python -m compileall scripts/ -q`.
- Run `pytest`.
- Run `pip install -e .` and import `DatagovClient`.

## Web validation scenarios

- Confirm the production base endpoint against the data.gov.il documentation page.
- Confirm no official webhook event surface is documented before adding webhook guidance.
- Confirm statutory rates, thresholds, and forms outside CKAN against the responsible Israeli authority on the access date.
- Confirm that sandbox examples use an environment variable rather than claiming an official sandbox host.
