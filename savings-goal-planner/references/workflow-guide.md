# Workflow Guide

## Workflow 1: Consumer major purchase

Use this workflow for a car, renovation, wedding, family event, or appliance replacement.

1. Define the target in today's ₪.
2. Set the payment date in DD/MM/YYYY.
3. Convert the date gap to months.
4. Add current savings already dedicated to the goal.
5. Add existing monthly deposits.
6. Select a conservative vehicle when the horizon is below 36 months.
7. Run the goal calculation.
8. Review the affordability warning.
9. Run a stress case with inflation 1 to 2 percentage points higher.
10. Store the goal when monthly review is needed.

Command:

```bash
savings-goal-planner goal \
  --name "Used delivery vehicle" \
  --target 180000 \
  --months 36 \
  --current-savings 40000 \
  --current-monthly 1500 \
  --inflation-rate 0.025 \
  --vehicle bank_deposit_fixed \
  --monthly-income 22000 \
  --format json
```

Decision rule:
- If required monthly saving is affordable, automate the transfer.
- If it exceeds 30 percent of income, extend the date, lower the target, or add an initial deposit.
- If the horizon is shorter than 12 months, avoid return assumptions that depend on market risk.

## Workflow 2: Freelancer equipment upgrade

Use this workflow for cameras, computers, machinery, software subscriptions paid annually, or professional tools.

1. Separate the gross invoice from recoverable VAT when relevant.
2. Decide whether the cash need is gross or net of VAT timing.
3. Add replacement date and warranty deadline.
4. Choose `money_market_fund` or `bank_deposit_fixed` for short horizons.
5. Keep business tax reserves in a separate goal.
6. Run base and delayed-payment scenarios.
7. Store the output with the assumption date.

Example:

```bash
savings-goal-planner create-goal \
  --name "Editing workstation" \
  --target 42000 \
  --months 18 \
  --current-savings 8000 \
  --current-monthly 900 \
  --vehicle money_market_fund \
  --env sandbox \
  --format json
```

Review checklist:
- Check whether the business can deduct depreciation or expense the purchase.
- Check VAT cash-flow timing.
- Confirm that the saving transfer does not reduce tax reserve coverage.

## Workflow 3: Small-business tax reserve

Use this workflow for VAT, income tax, and National Insurance reserves.

1. Estimate monthly gross receipts.
2. Estimate VAT payable separately from income-tax and National Insurance exposure.
3. Use separate goals for each reserve type.
4. Use `cash_bank` for near-term payments and `money_market_fund` only when timing allows.
5. Avoid market-risk vehicles for statutory payments.
6. Store each reserve goal with an explicit environment and store path.

Example:

```bash
savings-goal-planner create-goal \
  --name "Quarterly VAT reserve" \
  --target 51000 \
  --months 3 \
  --vehicle cash_bank \
  --env production \
  --format json
```

Control rule:
- Do not combine statutory reserves with discretionary purchase goals.
- Recalculate after a large invoice, expense change, or VAT filing.

## Workflow 4: Retirement gap

Use this workflow for a simplified retirement gap in today's ₪.

1. Enter current age, retirement age, and longevity target.
2. Enter desired retirement spending in today's ₪.
3. Enter expected pension or allowance income in today's ₪.
4. Enter current retirement savings.
5. Use real return assumptions.
6. Run a base case and a low-return case.
7. Run longevity stress to ages 95 and 100.
8. Treat the output as an estimate requiring professional pension review.

Command:

```bash
savings-goal-planner retirement \
  --current-age 42 \
  --retirement-age 67 \
  --life-expectancy 95 \
  --monthly-spending 14000 \
  --expected-pension 7000 \
  --current-savings 180000 \
  --accumulation-return 0.04 \
  --retirement-return 0.025 \
  --format json
```

Decision rule:
- If monthly gap is zero, review whether the pension estimate is realistic.
- If required monthly saving is too high, adjust retirement age, spending target, current contributions, or expected income.
- Do not use purchase-goal vehicle ranking for retirement decisions.

## Workflow 5: Vehicle comparison

Use this workflow to rank informational vehicle candidates.

1. Choose horizon in months.
2. Choose maximum risk tolerance.
3. Choose liquidity need.
4. Mark tax-advantaged availability only after eligibility is checked.
5. Review the top candidates and cautions.
6. Replace preset returns with product-specific assumptions before production use.

Command:

```bash
savings-goal-planner recommend-vehicles \
  --months 72 \
  --risk medium \
  --liquidity few_days \
  --tax-advantaged \
  --format json
```

Decision rule:
- Select the vehicle with the best fit, not the highest return.
- Reject candidates whose liquidity conflicts with payment timing.
- Reject retirement-only wrappers for ordinary purchases.

## Workflow 6: Stored goal monitoring

Use this workflow for a goal that must be revisited monthly.

1. Create the stored goal.
2. Extract the `id`.
3. Retrieve the same goal by `id`.
4. Update the store externally only through a controlled process.
5. Recalculate by creating a new goal when assumptions change.
6. Keep old records for audit and comparison.

Command chain:

```bash
CREATE_RESPONSE="$(savings-goal-planner create-goal \
  --name "Office renovation" \
  --target 90000 \
  --months 30 \
  --current-savings 25000 \
  --env sandbox \
  --format json)"

GOAL_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"

savings-goal-planner show-goal --id "$GOAL_ID" --env sandbox --format json
```

Operational rule:
- Use `sandbox` for examples, drafts, and training.
- Use `production` only for controlled internal use.
- Use a custom `--store` path for repeatable tests and shared automation.

## Review calendar

| Trigger | Action |
|---|---|
| Interest-rate change | Refresh deposit and money-market assumptions |
| CPI publication | Refresh inflation scenario |
| Tax-year start | Refresh tax caps and reserve assumptions |
| Large invoice issued | Recalculate business reserves |
| Major price quote changes | Recalculate purchase goal |
| Market drawdown | Reassess risky vehicle fit for near-term goals |
| Life event | Reassess retirement and emergency reserve assumptions |
