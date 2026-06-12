# Troubleshooting Guide

Use this playbook when validation fails, the Tax Authority API returns an error, or a business user cannot decide how to handle a held invoice.

## First triage

1. Identify the environment: sandbox or production.
2. Record the endpoint URL and HTTP status.
3. Save the request payload, response payload, timestamp, operator identity, and VAT dealer number.
4. Classify the issue as data validation, authorization, endpoint routing, business refusal, or Tax Authority outage.
5. Avoid issuing a final invoice above the threshold until the classification is complete.

## Data validation failures

| Check | Expected value | Fix |
|---|---|---|
| VAT number length | 9 digits | Remove punctuation and leading spaces; preserve leading zeros. |
| VAT check digit | Israeli identity-number checksum passes | Correct the dealer number before sending. |
| Invoice date | `YYYY-MM-DD` | Convert from DD-MM-YYYY only for display, not API submission. |
| Date range | Not too old and not too far ahead | Use actual document date and confirm retroactive rules. |
| Discount | Absolute positive amount | Never send a negative discount. |
| VAT math | `payment_amount * 0.18` unless zero-rate/exempt | Recalculate with 2 decimal rounding. |
| Total | `payment_amount + vat_amount` | Fix rounding and line summary totals. |
| Threshold | Before VAT | Do not test against total including VAT. |

## Authorization failures

### `401 Unauthorized`

Actions:

1. Refresh the OAuth2 access token.
2. Confirm the token was issued for the intended environment.
3. Confirm the token includes the relevant service permission.
4. Retry once after refresh.

### `403 Forbidden`

Actions:

1. Confirm the operator has permission to act for the seller VAT number.
2. Confirm corporation authorization if a company or partnership is involved.
3. Confirm the requested service is enabled for the operator.
4. Re-run the authorization flow from the Tax Authority service if needed.

### `406 Not Acceptable`

Actions:

1. Check whether `vat_number` or `customer_vat_number` is outside the authorized scope.
2. Confirm the customer VAT number is a valid Israeli VAT dealer number.
3. Avoid masking authorization problems as payload problems.

## Endpoint routing failures

| Symptom | Cause | Fix |
|---|---|---|
| 404 on approval | Wrong host or path | Use `/shaam/tsandbox/Invoices/v2/Approval` or `/shaam/production/Invoices/v2/Approval`. |
| 404 on invoice details | Production service uses `openapi.taxes.gov.il` for invoice-information | Route lookup calls to the documented production host. |
| Sandbox token rejected in production | Mixed credentials | Keep separate secrets and config files for each environment. |
| HTML response instead of JSON | Wrong portal URL instead of API URL | Use API endpoint, not the human portal page. |

## Business refusals

A business refusal is not the same as a technical failure. Do not retry with altered invoice identifiers to bypass controls.

When a refusal appears:

1. Display the refusal reason and error list.
2. Lock the original `invoice_id` and payload in the audit trail.
3. Present the allowed alternatives: cancel, continue without deductible input VAT, reverse charge, or hearing.
4. Submit the selected decision through the decision API where required.
5. Print required notices on the invoice if continuing without allocation or using reverse charge.

## Batch allocation problems

Batch requests can partially succeed. Treat each invoice independently after receiving a batch response.

- Approved invoice: store confirmation number and proceed.
- Failed invoice: fix the specific invoice and resubmit it separately.
- Main batch error: correct summary fields such as invoice count and aggregate totals.
- Duplicate decision error: locate the original held-invoice record before submitting a new decision.

## Recipient-side verification problems

When a customer cannot verify a supplier invoice:

1. Request the full allocation number and the right-most 9 digits.
2. Confirm seller VAT number, buyer VAT number, invoice date, amount before VAT, and VAT amount.
3. Try the invoice-information details service with allocation number.
4. Try confirmation-number lookup only if the invoice details match exactly.
5. Treat a zero confirmation result as unresolved until the supplier or Tax Authority clarifies it.

## Incident log template

```text
Environment:
Endpoint:
HTTP status:
API status:
Invoice ID:
Seller VAT number:
Customer VAT number:
Invoice date:
Payment amount before VAT:
VAT amount:
Operator identity:
Error code:
Error parameter:
Business decision:
Next action owner:
```
