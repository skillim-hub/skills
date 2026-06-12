# Troubleshooting

## Quick diagnosis table

| Problem | Likely cause | Fix |
|---|---|---|
| `unknown treatment code` | Clinic wording was pasted directly | Map wording to supported code or extend the catalog |
| Cost is lower than clinic quote | Missing imaging, lab, temporary crown, surgery, sedation, specialist, medication, or follow-up | Add missing items and quote exclusions |
| Cost is higher than clinic quote | Quantity is duplicated or provider/region factor is too conservative | Check tooth count, quantity, and provider profile |
| Coverage is zero | Waiting period not met, category not covered, or annual cap exhausted | Update insurance fields |
| Annual cap behaves strangely | `used_annual_ils` exceeds `annual_limit_ils` | Correct benefit data |
| Schedule starts on wrong date | Date format mismatch | Use DD/MM/YYYY, such as 15/07/2026 |
| VAT is included unexpectedly | `include_vat=true` | Set to false unless taxable invoice modeling is required |
| CLI import error | Command is run from a copied script without the client file beside it | Keep both scripts in the same `scripts/` folder |
| Typer command missing | Dev dependencies not installed | Run `pip install -r requirements-dev.txt` |
| Pytest cannot find tests | Wrong working directory | Run `python -m pytest -q` from package root |
| Hebrew output looks unnatural | Machine translation or mixed terminology | Use `SKILL_HE.md` wording and avoid transliteration |
| Provider comparison looks like official pricing | Default factors were not replaced with current tariffs | Import dated local price data and display source date |

## Clinical red flags

Stop cost optimization and recommend same-day clinical triage when the user reports:

- Facial swelling.
- Fever.
- Trauma.
- Uncontrolled bleeding.
- Rapidly worsening pain.
- Difficulty swallowing or breathing.
- Post-operative infection symptoms.
- Numbness or spreading swelling.

Do not provide diagnosis. State that urgent symptoms require dental or emergency medical evaluation.

## Pricing issues

### Missing crown after root canal
Root canal cost may not include crown. Ask:

- Is a crown required for this tooth?
- Is a temporary restoration included?
- What material is planned?
- Is lab work included?

### Implant price gap
Implant quotes vary because they may include or exclude:

- Extraction.
- Bone graft.
- Sinus lift.
- CBCT or panoramic imaging.
- Surgical guide.
- Implant crown.
- Temporary prosthesis.
- Sedation.
- Follow-up visits.

### HMO and supplementary-plan mismatch
Confirm:

- Current membership.
- Supplementary-plan tier.
- Waiting periods.
- Age-specific benefits.
- Annual cap.
- Whether the clinic participates in the relevant plan.
- Whether the specific dentist or specialist is included.

## Data-entry problems

### Treatment quantity
Use `quantity` only when the same treatment repeats. Use separate rows when tooth numbers differ and notes matter.

Bad:

```json
{"code": "filling_small", "quantity": 4}
```

Better:

```json
[
  {"code": "filling_small", "tooth": "16"},
  {"code": "filling_small", "tooth": "26"},
  {"code": "filling_small", "tooth": "36"},
  {"code": "filling_small", "tooth": "46"}
]
```

### Date format
Use `DD/MM/YYYY` in Hebrew-facing workflows. ISO `YYYY-MM-DD` is accepted by the client, but local-facing outputs use `DD/MM/YYYY`.

### Override price
Use `override_price_ils` only when a clinic gave a written price for a specific item. Avoid mixing official tariff rows with guessed overrides without notes.

## CLI troubleshooting

```bash
python scripts/dental-treatment-planner-cli.py sample --output plan.json
python scripts/dental-treatment-planner-cli.py validate plan.json
python scripts/dental-treatment-planner-cli.py validate plan.json --strict
python scripts/dental-treatment-planner-cli.py estimate plan.json --markdown
python scripts/dental-treatment-planner-cli.py catalog export catalog.csv
```

## Production fixes

- Replace default catalog values with dated source rows.
- Add source quality labels: written quote, provider publication, user-provided screenshot, estimated default.
- Keep old price tables for audit, but mark them inactive.
- Add manual review queue for implant, orthodontic, full-mouth rehabilitation, and emergency cases.
- Block output that implies medical certainty.
