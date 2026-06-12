# Migration Checklist

## Inventory

- List current source files.
- Record source URLs.
- Record export dates.
- Record reporting periods.
- Mark official and non-official sources.
- Preserve raw files.

## Column mapping

| Existing column | Canonical field | Required | Notes |
|---|---|---:|---|
| מספר קופה | `fund_id` | Yes | Keep as text |
| שם קופה | `fund_name` | Yes | Preserve Hebrew |
| תאריך דיווח | `report_date` | Yes | Convert internally |
| תשואה חודשית | `monthly_return_pct` | No | Percentage points |
| דמי ניהול מהפקדה | `management_fee_deposit_pct` | No | Percentage points |
| דמי ניהול מצבירה | `management_fee_assets_pct` | No | Percentage points |

## Replace formulas

| Old spreadsheet step | New client/CLI step |
|---|---|
| Latest row lookup | `latest_by_fund` |
| Sort top returns | `rank(..., metric="trailing_36m_return_pct")` |
| Sort lowest fees | `rank(..., metric="management_fee_assets_pct", ascending=True)` |
| Fee simulation | `estimate_fee_impact` |
| Data checks | `validate_records` |

## Parity validation

- Run old spreadsheet on a fixed file.
- Run enhanced client on the same file.
- Compare row counts.
- Compare selected fund IDs.
- Compare key metrics.
- Document differences from duplicate handling, date parsing, and latest-record logic.

## Wording migration

| Replace | With |
|---|---|
| Best fund | Highest reported metric in this dataset |
| Recommended | Shown for information only |
| Move to | Compare with a licensed adviser before personal decisions |
| Guaranteed | Reported historical |

## Production readiness

- No private personal data in samples.
- No recommendations in templates.
- Official source URLs are documented.
- Export date and reporting period are visible.
- Hebrew output uses `₪` and `DD-MM-YYYY`.
- Tests pass.
- CLI commands are documented.

## Rollback

Keep the previous process available until:
- Three representative files pass validation.
- One Hebrew and one English report are reviewed.
- Edge cases are documented.
- Neutral wording is accepted.

## Version migration notes

From `0.1.0` stub to `1.0.0`:
- Added full guides.
- Added API/reference documentation.
- Added workflow, troubleshooting, test scenario, and migration references.
- Added typed client, CLI, tests, examples, packaging metadata, README, changelog, and license.
- Removed non-neutral metadata, presentation, and distribution phrasing.
