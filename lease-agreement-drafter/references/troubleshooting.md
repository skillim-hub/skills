# Troubleshooting

## Import fails after installation

Run:

```bash
pip install -e .
python -c "from lease_agreement_drafter import LeaseAgreementDrafterClient; print('ok')"
```

If the import still fails, confirm that the command runs from the package root and that the virtual environment is active.

## CLI command is missing

Run:

```bash
pip install -e .
lease-agreement-drafter schema --env sandbox
```

If the command is still missing, check that the virtual environment `bin` or `Scripts` directory appears in the shell path.

## Hebrew output shows escaped characters

Use `json.dumps(payload, ensure_ascii=False, indent=2)` when printing JSON. Do not pipe the output through tools that force ASCII escaping.

## Residential security warning appears

The draft appears to be a covered apartment lease and the security amount may exceed the common cap. Reduce the security or obtain legal review before signing.

## VAT warning appears on an apartment lease

Residential apartment rent for periods up to 25 years is generally VAT-exempt. Remove VAT unless a tax professional confirms a specific exception.

## Office use warning appears

Add a precise permitted use. Example: `משרד ייעוץ ועיצוב ללא קבלת קהל חריגה`. Check zoning, licensing, accessibility, signage, and building rules.

## Date validation fails

Use DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD. The package normalizes stored dates to DD/MM/YYYY.

## Draft status is `needs_review`

At least one error-level finding exists. Correct missing party names, missing address, missing rent, or invalid dates before treating the draft as usable.

## Template audit returns several warnings

Warnings mean common operational clauses are missing. Add repair timing, handover protocol, and balanced early termination language. Run the audit again after editing.

## Pytest cannot find pytest-asyncio

Install development requirements:

```bash
pip install -r requirements-dev.txt
```

## Protected tenancy appears

Stop using the generated draft. Escalate for specialist review if any party mentions key money, protected tenant status, historic tenancy, or protected tenancy rights.

## Municipal tax allocation is unclear

Check the municipality classification and billing method. State who pays arnona, when account transfer occurs, and what happens if classification changes.

## Management fee is unclear

State the monthly amount or calculation method, VAT treatment, payment date, services included, audit rights, and whether extraordinary works are excluded.

## Guarantor details are missing

Add guarantor names, identifiers, addresses, and signature blocks, or remove the guarantor section.

## The generated draft is too general

Add more facts: registry details, permitted use, defects, inventory, payment method, insurance requirements, option conditions, and special conditions.
