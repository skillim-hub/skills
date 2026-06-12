# Migration Checklist

Use this checklist when replacing a spreadsheet, manual monitoring routine, legacy listening tool, or earlier package version.

## 1. Inventory current process

- [ ] List all sources.
- [ ] Identify exporter and owner for each source.
- [ ] Identify format: CSV, JSON, XLSX, manual copy, screenshot, vendor dashboard.
- [ ] Identify who replies to customers.
- [ ] Identify raw-file storage location.
- [ ] Identify current retention period.
- [ ] Identify unnecessary personal data.
- [ ] Collect current response templates.

## 2. Clean source list

- [ ] Remove private or unauthorized sources.
- [ ] Replace scraping with approved exports or APIs where available.
- [ ] Document source owner and access method.
- [ ] Add platform-term review date.
- [ ] Define manual fallback for API outages.

## 3. Migrate keywords

- [ ] Import official Hebrew names.
- [ ] Add English names.
- [ ] Add spelling mistakes.
- [ ] Add public owner/professional names only when they are brand identifiers.
- [ ] Add products and campaigns.
- [ ] Add local identifiers.
- [ ] Add exclusions for common false positives.
- [ ] Test with historical data.

## 4. Migrate historical mentions

- [ ] Export historical records to CSV or JSON.
- [ ] Convert dates to DD/MM/YYYY or ISO.
- [ ] Normalize source names.
- [ ] Remove unneeded fields.
- [ ] Redact personal data where possible.
- [ ] Deduplicate by URL or normalized hash.
- [ ] Mark imported records as `historical`.

## 5. Migrate sentiment labels

| Legacy label | New label |
|---|---|
| `good`, `praise`, `positive_he` | `positive` |
| `bad`, `complaint`, `negative_he` | `negative` |
| `question`, `info`, `mention` | `neutral` |
| `both`, `mixed_review` | `mixed` |
| `crisis`, `legal`, `safety` | `urgent` |

## 6. Migrate workflows

- [ ] Convert spreadsheet comments to `notes`.
- [ ] Convert owner initials to operational owner names.
- [ ] Add `status`: open, waiting, resolved, document_only.
- [ ] Add `due_date`.
- [ ] Add `human_review_required`.
- [ ] Add `recommended_action`.

## 7. Validate

- [ ] Run at least 20 test scenarios.
- [ ] Compare old/new sentiment distribution.
- [ ] Inspect top false positives.
- [ ] Inspect top false negatives.
- [ ] Inspect all urgent items.
- [ ] Verify Hebrew encoding.
- [ ] Verify report formatting.
- [ ] Verify ₪ and DD/MM/YYYY localization.

## 8. Rollout

- [ ] Run old and new processes in parallel for one week.
- [ ] Review differences daily.
- [ ] Update templates.
- [ ] Train support staff on response categories.
- [ ] Freeze old process.
- [ ] Archive legacy raw exports according to retention rules.
- [ ] Document migration date.

## 9. Rollback

- [ ] Preserve last known good keyword map.
- [ ] Preserve legacy export templates.
- [ ] Preserve owner escalation list.
- [ ] Preserve response templates.
- [ ] Keep read-only historical archive.
- [ ] Define rollback approver.

## 10. 30-day review

- [ ] Compare urgent detection accuracy.
- [ ] Compare response time.
- [ ] Compare unresolved complaint count.
- [ ] Remove unused keywords.
- [ ] Add new slang/campaign terms.
- [ ] Update retention and access review.
