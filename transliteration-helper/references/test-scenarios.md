# Test scenarios

Use these scenarios for QA, regression testing, and manual review training.

| # | Scenario | Input | Expected/Review target | Notes |
|---:|---|---|---|---|
| 1 | Common first name | `דוד` | `DAVID` | Known-name override |
| 2 | Common full name | `דוד כהן` | `DAVID KOHEN` | Two overrides |
| 3 | Title case invoice | `שרה לוי` | `Sara Levi` | Use `--case title` |
| 4 | Maqaf | `בן־דוד` | `BEN-DAVID` | Normalize maqaf |
| 5 | Standard hyphen | `בן-דוד` | `BEN-DAVID` | Preserve hyphen |
| 6 | Tzadi default | `צבי` | `ZVI` | Default צ style |
| 7 | Tzadi alternate | `צבי` | `TZVY` in strict mode with `--tzadi-style tz` | Integration-specific |
| 8 | Passport variant | `כהן` | `KOHEN`; review if `COHEN` exists | Preserve official spelling |
| 9 | Mixed script | `דוד Cohen` | `DAVID COHEN` + warning | Review source |
| 10 | Latin only | `David Cohen` | `DAVID COHEN` + warning | Treat as existing Latin |
| 11 | Empty input | whitespace | validation error | Reject row |
| 12 | Pointed bet with dagesh | `ברק` | `BARAK` | Dagesh controls B |
| 13 | Pointed bet without dagesh | `ברק` | `VARAK` when no override | Dagesh missing |
| 14 | Shin | `שלום` | `SHALOM` | Shin dot |
| 15 | Sin | `שרה` | `SARA` | Sin dot |
| 16 | Shuruk | `רות` | `RUT` | Vav with dagesh as U |
| 17 | Loan letter | `ג׳ורג׳` | `GEORGE` | Geresh |
| 18 | Unknown with ו | `אורבל` | warning | Could need override |
| 19 | Unknown with ב/כ/פ | `אבתיה` | dagesh warning | Manual review |
| 20 | CSV missing column | CSV without `hebrew_name` | validation error | Use `--input-column` |
| 21 | Batch text | text lines `דוד`, `שרה` | two output rows | CLI batch |
| 22 | Batch CSV | `hebrew_name` column | JSON/CSV rows | Integration test |
| 23 | Existing official spelling | Hebrew plus stored `COHEN` | preserve `COHEN` | Do not regenerate |
| 24 | Apostrophe restriction | `ג׳ורג׳` for legacy system | canonical `GEORGE`; export-safe value if needed | Integration transform |
| 25 | Long double family name | `כהן-לוי` | review | Confirm official hyphenation |
| 26 | Business descriptor | `דוד כהן חשמלאי` | transliterate name, translate descriptor separately | Not all text is a name |
| 27 | Consumer booking | `חנה` | `HANA`; review if `CHANA` exists | Travel forms need official spelling |
| 28 | Duplicate detection | `KOHEN` vs `COHEN` | flag duplicate | Use stable identifiers |
| 29 | Lowercase export | `משה כהן` | `moshe kohen` | Use `--case lower` |
| 30 | Explain trace | `דוד` with `--explain` | token rule trace present | Audit/debugging |

## Automated smoke-test commands

```bash
python scripts/transliteration-helper-cli.py transliterate "דוד כהן"
python scripts/transliteration-helper-cli.py transliterate --format json --explain "ג׳ורג׳ כהן"
python scripts/transliteration-helper-cli.py validate "אבתיה"
python scripts/transliteration-helper-cli.py transliterate --strict --tzadi-style tz "צבי"
pytest -q
```

## Manual review samples

Use these names for reviewer calibration:

```text
כהן
חנה
יצחק
צבי
מיכאל
אבתיה
אורבל
דוד Cohen
בן־דוד
ג׳ורג׳
```

For each sample, record:

- Generated Latin output.
- Warning codes.
- Reviewer decision.
- Final approved spelling.
- Source of approval.
- Date in `DD/MM/YYYY`.
