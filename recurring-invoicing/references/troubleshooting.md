# Troubleshooting Guide

## Tax ID problems

### Symptom

The customer or business tax ID fails validation.

### Causes

- Leading zeros were removed.
- Digits were copied with separators.
- A private ID was entered where a company or dealer number was expected.
- The checksum is wrong.

### Resolution

1. Strip non-digits.
2. Left-pad to nine digits.
3. Run checksum validation.
4. Confirm the legal identifier with the customer or accountant.
5. Update the customer master record before invoice generation.

## VAT amount mismatch

### Symptom

The invoice total differs from the bookkeeping system by one agora or more.

### Causes

- Floating-point arithmetic.
- Rounding performed only at the final total.
- Wrong issue date used for VAT rate.
- Mixed exempt and taxable lines handled incorrectly.

### Resolution

1. Use Decimal values.
2. Round money values to two decimals.
3. Confirm the VAT rate by issue date.
4. Calculate VAT line by line when required by policy.
5. Compare sample invoices with the accounting system.

## Duplicate invoices

### Symptom

The same subscription generated more than one invoice for the same period.

### Causes

- Retry job reran without checking stored state.
- Invoice ID sequence was not persisted.
- Payment event and invoice run both generated a document.

### Resolution

1. Use a unique key: subscription ID plus billing period.
2. Store invoice candidate state before external calls.
3. Reuse idempotency keys on retries.
4. Block generation when an issued invoice already exists.

## Allocation required unexpectedly

### Symptom

An invoice that would not have required allocation earlier in 2026 now requires one.

### Causes

- The default threshold dropped from ₪10,000 to ₪5,000 on 01/06/2026.
- The invoice issue date is later than the service-period date.
- The invoice is a tax invoice or tax invoice receipt rather than a receipt.

### Resolution

1. Run `threshold_for_issue_date(issue_date)`.
2. Confirm the issue date printed on the invoice.
3. Compare the subtotal before VAT, not the total including VAT.
4. Ask accounting to approve any override.

## Allocation skipped unexpectedly

### Symptom

A high-value document is not marked as requiring allocation.

### Causes

- Document type is receipt, pro forma, or another non-eligible type in the helper.
- Subtotal before VAT is below the effective threshold for the issue date.
- Customer is not marked or treated as an authorized dealer in business workflow.
- A custom threshold mapping was supplied.

### Resolution

1. Confirm document type.
2. Confirm issue date and effective threshold.
3. Confirm customer VAT status.
4. Remove stale custom threshold configuration.

## Allocation rejected

### Symptom

The allocation service returns a validation error.

### Causes

- Payload schema changed.
- Local helper payload was sent directly instead of being mapped to official lowercase fields.
- Business is not enabled for production.
- Customer tax ID is invalid.
- Required software identifier is missing.

### Resolution

1. Compare request body to the current official schema.
2. Verify environment and credentials.
3. Validate all tax IDs.
4. Confirm threshold calculation uses subtotal before VAT.
5. Store the raw error and escalate if official behavior changed.

## Allocation service unavailable

### Symptom

The gateway times out or returns a server error.

### Causes

- External outage.
- Network failure.
- Rate limiting.
- Incorrect retry strategy.

### Resolution

1. Keep the invoice in candidate state.
2. Queue the request.
3. Retry with the same client transaction ID.
4. Use backoff and jitter.
5. Alert the operator after the configured retry limit.

## Held invoice endpoint uncertainty

### Symptom

A developer cannot determine the correct endpoint for the held-invoice decision service from public PDFs.

### Cause

The checked English and Hebrew public API documents show different path naming for the decision service.

### Resolution

1. Do not hard-code the path from public PDFs.
2. Verify the endpoint in the registered Tax Authority developer portal.
3. Keep the adapter endpoint configurable by environment.
4. Record the verified endpoint and access date in local implementation notes.

## Month-end drift

### Symptom

A subscription that started on the 31st continues on the 28th after February.

### Cause

Month-end anchor was not preserved.

### Resolution

Enable month-end preservation. Validate generated dates around February and leap years.

## Credit note total is wrong

### Symptom

The credit tax invoice does not fully reverse the original invoice.

### Causes

- Credit was calculated from current price instead of original invoice.
- VAT rate changed after the original invoice.
- The original discount or exemption flag was not copied.

### Resolution

1. Create the credit from the original immutable invoice.
2. Preserve original VAT rates and line treatment.
3. Link the credit to the original invoice ID.
4. Review with accounting before delivery.
