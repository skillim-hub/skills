# Migration Checklist

Use this checklist when replacing manual spreadsheets, ad hoc scripts, or the original basic helper with the enhanced CBS Data Analyzer.

## Inventory existing usage

- [ ] List every spreadsheet, script, and prompt that uses CBS data.
- [ ] Record the source URL for each statistic.
- [ ] Record every hard-coded index code.
- [ ] Identify contract-sensitive calculations.
- [ ] Identify dashboards or reports that show "latest" without reference period.
- [ ] Identify Hebrew outputs that need `₪` and `DD/MM/YYYY`.

## Replace hard-coded values

- [ ] Remove static CPI, wage, unemployment, and housing values from prompts.
- [ ] Fetch live values from official endpoints where possible.
- [ ] Store fixture values only for tests and examples.
- [ ] Add retrieval date to generated outputs.
- [ ] Add source URL and series code to every calculation.

## Standardize formulas

- [ ] Use `amount × target_index / base_index` for index-linked amounts.
- [ ] Validate base index is positive.
- [ ] Apply cap, floor, and rounding rules only when explicitly known.
- [ ] Separate VAT from indexation unless the contract specifies otherwise.
- [ ] Keep index levels distinct from percentage changes.

## Upgrade scripts

- [ ] Use `scripts/cbs_data_analyzer_client.py` for reusable sync and async calls.
- [ ] Use `scripts/cbs_data_analyzer_cli.py` for command-line workflows.
- [ ] Move one-off calculations into examples or tests.
- [ ] Add mocked HTTP tests before enabling live calls in automation.
- [ ] Configure timeouts and retries in scheduled jobs.

## Migrate data.gov searches

- [ ] Replace generic searches with `fq=organization:lamas`.
- [ ] Read dataset metadata before using resources.
- [ ] Preserve dataset title, identifier, modified date, and license.
- [ ] Do not assume data.gov has CPI time series; use CBS Price Indices API.

## Documentation controls

- [ ] Link to `references/api-reference.md` from internal runbooks.
- [ ] Add `references/troubleshooting.md` to support documentation.
- [ ] Use `references/test-scenarios.md` as acceptance criteria.
- [ ] Keep `CHANGELOG.md` updated for breaking changes.

## Release readiness

- [ ] Run `pytest scripts/test_cbs_data_analyzer_client.py`.
- [ ] Run CLI smoke tests offline with mocked or manual sample values.
- [ ] Inspect package for branding strings, visual assets, creator metadata, and stale snapshots.
- [ ] Verify `metadata.json` has no creator-attribution field.
- [ ] Verify the license file uses the required neutral rights-holder line.
- [ ] Zip the skill root and publish the archive.
