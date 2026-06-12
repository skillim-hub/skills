# Migration checklist

Use this checklist when adding transliteration to an existing customer, supplier, freelancer, or consumer database.

## 1. Inventory existing fields

Identify:

- Hebrew name field.
- Latin name field, if any.
- Customer ID, supplier ID, email, phone, tax number, or other stable identifier.
- Source of existing Latin spelling.
- Last update date.
- Downstream systems that consume the name.

## 2. Classify existing Latin spelling

Use a source rank:

| Rank | Source | Action |
|---:|---|---|
| 1 | Passport, official certificate, signed contract, bank record | Preserve exactly |
| 2 | Customer-confirmed spelling | Preserve unless a stronger source appears |
| 3 | Existing operational system | Preserve but review during migration |
| 4 | Generated transliteration | Regenerate only if policy changed |
| 5 | Unknown | Compare with generated output and review differences |

## 3. Export backup

Before any bulk update:

- Export source data.
- Export generated results.
- Export diff report.
- Store rollback files with date, for example `backup_customers_03/06/2026.csv`.

## 4. Run dry-run transliteration

Create a new file rather than updating the live system.

```bash
python scripts/transliteration-helper-cli.py batch \
  -i customers.csv \
  --input-column hebrew_name \
  --format csv \
  -o customers_transliterated_dry_run.csv
```

## 5. Build review queues

Create these queues:

| Queue | Trigger |
|---|---|
| Official spelling exists and differs | Existing official value differs from generated value |
| Warning present | Any warning code exists |
| Mixed script | Hebrew and Latin appear together |
| Long or special characters | Downstream system may reject |
| Business descriptor | Input may include profession or business text |

## 6. Apply update rules

Use this order:

1. Preserve official Latin spelling.
2. Preserve customer-confirmed spelling.
3. Use approved manual review value.
4. Use generated spelling with no warnings.
5. Keep pending when warnings exist and no review is complete.

## 7. Record audit fields

Recommended fields:

| Field | Example |
|---|---|
| `latin_name` | `DAVID KOHEN` |
| `latin_source` | `system-generated` |
| `latin_policy_version` | `1.0.0` |
| `latin_review_status` | `approved` |
| `latin_reviewed_by` | `operations` |
| `latin_review_date` | `03/06/2026` |
| `latin_warnings` | `unpointed_hebrew_ambiguous_vowels` |

## 8. Test downstream integrations

Check:

- Maximum field length.
- Uppercase/lowercase requirements.
- Hyphen acceptance.
- Apostrophe acceptance.
- CSV encoding (`UTF-8`).
- Duplicate customer matching.
- Invoice rendering.
- Search behavior in CRM.
- Export behavior to payment providers and shipping systems.

## 9. Rollout plan

1. Start with a small sample.
2. Review all warnings.
3. Import into a staging environment.
4. Compare search, billing, and export behavior.
5. Create rollback instructions.
6. Run production import.
7. Monitor duplicate records and rejected exports.
8. Freeze automatic overwrites after rollout.

## 10. Post-migration controls

- Require source labels for every Latin spelling.
- Add a manual review queue for new warnings.
- Prevent overwriting official spellings.
- Keep versioned policy notes.
- Re-test when integration rules change.
