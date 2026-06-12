# Workflow Guide

## Workflow 1: Employee asks whether to sell options

1. Collect grant agreement, trustee confirmation, option ledger, exercise price, expected sale price, and sale date.
2. Enter the scenario with `track="102_capital"` only when trustee status is documented.
3. Calculate the earliest preferred sale date.
4. If sale is earlier than the preferred date, run a second scenario using ordinary-income treatment.
5. Compare net proceeds and warning flags.
6. Provide a written summary with assumptions, missing documents, and estimated tax components.

## Workflow 2: Small business preparing payroll support

1. Confirm whether the company plan is an approved Section 102 plan.
2. Request trustee export by employee and grant.
3. Match employee sale notices to payroll month.
4. Run calculations for each employee sale.
5. Separate employment income from capital gain.
6. Reconcile withholding already deducted by the trustee.
7. Store calculation output with payroll evidence.

## Workflow 3: Freelancer or consultant with option grant

1. Do not assume Section 102 applies.
2. Classify as Section 3(i), non-employee, or unknown until documents prove otherwise.
3. Model spread as ordinary income.
4. Add National Insurance and health contribution estimates when the income is business or employment-like.
5. Request professional review for VAT, withholding, and expense deductibility.

## Workflow 4: Public-company RSU sale

1. Confirm public-company status at grant.
2. Obtain grant-date fair market value.
3. Confirm trustee track and holding period.
4. Split grant-date value from later appreciation.
5. Compare result with trustee withholding certificate.

## Workflow 5: Foreign broker proceeds

1. Capture quantity, date, price, fees, and withholding in original currency.
2. Convert gross proceeds, basis, and FMV using appropriate ILS exchange rates.
3. Avoid using net cash after withholding as gross proceeds.
4. Keep FX source and date with the calculation file.

## Refresh official constants

1. Open `references/verification-log.md` and identify every rate or threshold used by the scenario.
2. Re-check the current Tax Authority and National Insurance pages for the requested tax year.
3. Override `TaxConstants` in Python when a client file, trustee certificate, or new official source uses a different tax year.
4. Store the source URL, access date, and quote with the exported case file.
