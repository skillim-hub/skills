# Troubleshooting

## Fast diagnosis table

| Symptom | Cause | Correction |
|---|---|---|
| `No relevant updates found` | Industry or keyword filters are too narrow | Run without keywords, lower minimum score, inspect raw source |
| All alerts look relevant to every sector | Sources use industry `all` | Add profile industries and keywords |
| Knesset bill appears as binding | Source hierarchy was not checked | Confirm final publication in Reshumot |
| Knesset OData returns maintenance or geo-block page | Network or endpoint access restriction | Retry from an allowed network, use official Knesset pages, and preserve the failure page |
| Rate or threshold conflicts across sources | Stale cached material or phased effective date | Prefer the newest official Tax Authority or Reshumot source and record the access date |
| Hebrew dates appear as month/day | Locale formatting mismatch | Use `format_il_date` and `DD/MM/YYYY` in Hebrew output |
| Duplicate alerts | Same update appears in HTML, RSS, and OData | Deduplicate by normalized title, URL, and publication date |
| Parser fails on gov.il page | Layout changed or content moved to PDF | Save raw HTML and add extraction rule |
| Empty PDF text | Scanned document | Use manual extraction or audited character recognition |
| High severity missing | Mandatory term not detected | Add Hebrew terms such as חובה, נדרש, עיצום, קנס |
| CLI cannot import package | Package not installed in editable mode | Run `pip install -e .` from the package root |
| Async example hangs | Remote source blocks requests | Use sandbox environment or configure polite timeouts |

## Import failures

Use the installable package path, not hyphenated module names.

Correct:

```python
from regulatory_update_notifier import RegulatoryMonitorClient
```

Incorrect:

```python
import regulatory-update-notifier-client
```

## Source failures

Use this order:

1. Confirm network access.
2. Open the official source in a browser.
3. Save the raw response.
4. Retry with sandbox fixtures.
5. Reduce request frequency.
6. Update parser mapping when the response shape changed.

## Classification failures

Check these signals:

- Source category: Reshumot, Knesset, regulator, consultation, enforcement.
- Mandatory terms: must, required, חובה, נדרש.
- Draft terms: draft, טיוטה, תזכיר, הערות הציבור.
- Enforcement terms: fine, penalty, קנס, עיצום, אכיפה.
- Dates and amounts: `DD/MM/YYYY`, `YYYY-MM-DD`, ₪ thresholds.

## Hebrew output issues

- Use `₪` before amounts where practical.
- Use `DD/MM/YYYY` in Hebrew prose.
- Prefer עצמאי over freelancer.
- Prefer מסחר מקוון over ecommerce.
- Prefer דוח over report in Hebrew prose.
- Avoid ניקוד in technical prose.

## Production recovery

When a production alert may be wrong:

1. Pause outbound notification.
2. Save source snapshot and generated summary.
3. Reclassify using source hierarchy.
4. Compare against Reshumot or official regulator page.
5. Reissue corrected digest with a clear correction note.
6. Add a test scenario for the failure mode.

## Web validation checklist

- Recheck tax rates, thresholds, forms, and official service pages before sending operational instructions.
- Use a second source for every confirmed row when changing package guidance.
- Mark unconfirmed example values as fixtures or remove them from public guidance.
