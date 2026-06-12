# Test Scenarios

Use these scenarios for manual QA, CLI testing, and automated regression coverage.

| # | Scenario | Input focus | Expected result |
|---:|---|---|---|
| 1 | Routine adult checkup | `exam`, `cleaning`, private center | Positive estimate, no dependency warning |
| 2 | Small filling with insurance | `filling_small`, 25% discount | Patient total lower than self-pay |
| 3 | Large filling without exam | `filling_large` only | Warning that exam is usually required |
| 4 | Molar root canal with X-ray | `exam`, `xray_bitewing`, `root_canal_molar` | Multi-visit estimate |
| 5 | Root canal without crown | Root canal only | Crown uncertainty should be mentioned in generated guidance |
| 6 | Crown only | `crown_porcelain` without exam | Dependency warning |
| 7 | Implant without imaging | `implant` only | Imaging warning |
| 8 | Implant staged plan | `panoramic_xray`, `implant`, `implant_crown` | High-cost multi-visit schedule |
| 9 | Emergency pain | Urgent extraction without `emergency_visit` | Same-day triage warning |
| 10 | Whitening before cleaning | `whitening` only | Cleaning/exam warning |
| 11 | Child fluoride | `exam`, `fluoride_child` | Low-cost preventive plan |
| 12 | Child sealants quantity 4 | `sealant_child`, quantity 4 | Quantity multiplied correctly |
| 13 | Orthodontic aligners | `orthodontic_consult`, `aligner_case` | Long schedule, high total |
| 14 | Denture plan | `denture_partial` | Multi-visit prosthetic estimate |
| 15 | Annual cap exhausted | `used_annual_ils` equals cap | Coverage zero |
| 16 | Annual cap partially used | Cap 3000, used 2500 | Coverage capped at 500 |
| 17 | Waiting period not met | `waiting_period_met=false` | Coverage zero |
| 18 | Covered categories only diagnostic | Preventive and diagnostic items | Discount only on diagnostic |
| 19 | Provider comparison | private, Maccabident, Clalit Smile | Sorted by patient total |
| 20 | Tel Aviv region | `region=tel_aviv` | Higher private estimate than periphery |
| 21 | Periphery region | `region=periphery` | Lower private estimate than center |
| 22 | VAT model enabled | `include_vat=true` | VAT amount and VAT warning |
| 23 | Invalid date | `07/15/2026` | Validation error |
| 24 | Empty treatment list | `[]` | Planner error |
| 25 | Unknown treatment code | `laser_magic` | Unknown-treatment error |
| 26 | Monthly visit cap | `max_visits_per_month=1` | Schedule spreads across months |
| 27 | Business-paid support | Minimal clinical details | Privacy and accountant warnings in guidance |
| 28 | Override price | `override_price_ils` | Estimate uses override |
| 29 | Senior complex rehab | Multiple crowns/denture | High-cost phased schedule |
| 30 | Quote comparison mismatch | Same tooth missing from one quote | Ask for apples-to-apples quote |

## CLI smoke tests

```bash
python scripts/dental-treatment-planner-cli.py sample --output /tmp/plan.json
python scripts/dental-treatment-planner-cli.py estimate /tmp/plan.json
python scripts/dental-treatment-planner-cli.py compare /tmp/plan.json
```

Strict implant warning:

```json
{
  "context": {"provider": "private", "region": "center", "strict": true},
  "treatments": [{"code": "implant"}]
}
```

Expected: non-zero exit or validation failure because imaging/exam dependencies are missing.
