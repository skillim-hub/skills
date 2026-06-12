# Test Scenarios

Use these scenarios to validate the skill, client, CLI, and examples.

## Scenario 1: Basic salary household

- Input: ₪15,000 income, ₪9,700 expenses
- Expected behavior: positive net cash flow and category totals

## Scenario 2: Monthly deficit

- Input: ₪10,000 income, ₪12,500 expenses
- Expected behavior: DEFICIT warning

## Scenario 3: Bi-monthly arnona

- Input: ₪900 arnona with normalize_months=2
- Expected behavior: monthly amount ₪450

## Scenario 4: Annual insurance

- Input: ₪4,800 insurance normalized over 12
- Expected behavior: monthly amount ₪400

## Scenario 5: Large cash withdrawal

- Input: ₪2,000 cash
- Expected behavior: cash review warning

## Scenario 6: Supermarket refund

- Input: ₪500 charge and ₪80 refund
- Expected behavior: net cost or refund tag

## Scenario 7: Installment purchase

- Input: ₪3,000 in 10 payments
- Expected behavior: monthly ₪300 and liability note

## Scenario 8: Food split

- Input: groceries and delivery mixed
- Expected behavior: split recommendation

## Scenario 9: Foreign currency

- Input: USD purchase plus ₪ settlement
- Expected behavior: use actual ₪ settlement

## Scenario 10: Shared rent

- Input: ₪7,000 rent, 50% share
- Expected behavior: budget user share ₪3,500

## Scenario 11: Emergency fund feasible

- Input: ₪12,000 gap, 8 months, ₪2,000 surplus
- Expected behavior: required ₪1,500 and feasible

## Scenario 12: Emergency fund infeasible

- Input: ₪20,000 gap, 5 months, ₪2,000 surplus
- Expected behavior: adjust date/target/category

## Scenario 13: Past due goal

- Input: due date already passed
- Expected behavior: past_due status

## Scenario 14: Goal complete

- Input: current exceeds target
- Expected behavior: complete status

## Scenario 15: Osek patur cash flow

- Input: ₪12,000 gross, no VAT
- Expected behavior: tax reserve reminder

## Scenario 16: Osek murshe VAT extraction

- Input: ₪11,800 gross at 18%
- Expected behavior: net ₪10,000 and VAT ₪1,800

## Scenario 17: Business software

- Input: ₪150 software tagged business
- Expected behavior: business subtotal separate

## Scenario 18: Mixed phone bill

- Input: ₪200, 50% business
- Expected behavior: split if basis provided

## Scenario 19: Missing tax reserve

- Input: business income without reserve
- Expected behavior: reserve warning

## Scenario 20: VAT rate missing

- Input: VAT requested with no rate
- Expected behavior: error or prompt

## Scenario 21: Duplicate CSV row

- Input: same date/vendor/amount/description twice
- Expected behavior: duplicate warning

## Scenario 22: Invalid date

- Input: 2026/05/01
- Expected behavior: INVALID_DATE

## Scenario 23: Unsupported currency

- Input: USD without ₪ settlement
- Expected behavior: conversion request

## Scenario 24: Internal transfer

- Input: checking to savings
- Expected behavior: transfer classification

## Scenario 25: Subscription detection

- Input: same vendor monthly
- Expected behavior: recurring charge flag

## Scenario 26: Other too large

- Input: other is 12% of spending
- Expected behavior: manual review warning

## Scenario 27: Empty category

- Input: known vendor but blank category
- Expected behavior: infer or uncategorized

## Scenario 28: Zero amount

- Input: amount 0
- Expected behavior: INVALID_AMOUNT

## Scenario 29: High debt payments

- Input: debt above 25% of income
- Expected behavior: DEBT_RISK

## Scenario 30: Paper budget only

- Input: category totals without transactions
- Expected behavior: summary plus lower-confidence note
