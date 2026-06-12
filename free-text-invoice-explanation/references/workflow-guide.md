# Workflow Guide

## Workflow 1: Explain a standard tax invoice line

Use for an authorized dealer charging a client for a service.

1. Confirm the document is a חשבונית מס or invoice-receipt.
2. Confirm the business is an עוסק מורשה or company.
3. Enter line description, quantity, unit price, and VAT rate.
4. Generate the explanation.
5. Review whether the service period is present.
6. Send the explanation next to the line item or in the payment email.

Example input:

```json
{
  "context": {
    "language": "he",
    "business_type": "authorized_dealer",
    "document_type": "tax_invoice",
    "document_date": "07/03/2026"
  },
  "lines": [
    {
      "description": "ייעוץ שיווקי חודשי",
      "quantity": "1",
      "unit_price": "1500",
      "vat_rate": "18"
    }
  ]
}
```

Expected explanation focus:

- What service was provided.
- Amount before VAT.
- VAT rate and VAT amount.
- Total payable for the line.

## Workflow 2: Explain a receipt from an exempt dealer

Use when a freelancer classified as עוסק פטור confirms payment.

1. Set `business_type` to `exempt_dealer`.
2. Set `document_type` to `receipt`.
3. Set VAT rate to `0`.
4. Explain that the receipt confirms payment and that VAT was not added.
5. Avoid saying that the customer may deduct VAT.

Example input:

```json
{
  "context": {
    "language": "he",
    "business_type": "exempt_dealer",
    "document_type": "receipt",
    "document_date": "07/03/2026"
  },
  "lines": [
    {
      "description": "עיצוב מצגת",
      "quantity": "1",
      "unit_price": "600",
      "vat_rate": "0"
    }
  ]
}
```

## Workflow 3: Explain reimbursement of an expense

Use when a business paid a cost on behalf of the client.

1. Mark the line as `reimbursable`.
2. Describe the supplier or cost type plainly.
3. Attach supporting documentation.
4. Do not invent the VAT treatment.
5. Use a detailed explanation when the client needs context.

Example input:

```json
{
  "context": {
    "language": "en",
    "business_type": "authorized_dealer",
    "document_type": "tax_invoice"
  },
  "options": {
    "language": "en",
    "detail_level": "detailed"
  },
  "lines": [
    {
      "description": "Courier fee paid on behalf of the client",
      "quantity": "1",
      "unit_price": "62.40",
      "vat_rate": "18",
      "reimbursable": true
    }
  ]
}
```

## Workflow 4: Explain a credit note

Use when a charge is reduced after the original invoice was issued.

1. Set `document_type` to `credit_note`.
2. Use a negative unit price when the source document stores credits as negative amounts.
3. Add a note identifying the original invoice or reason.
4. Explain that the line reduces or reverses a previous charge.
5. Keep a link to the original document in the accounting system.

Example input:

```json
{
  "context": {
    "language": "he",
    "business_type": "authorized_dealer",
    "document_type": "credit_note"
  },
  "lines": [
    {
      "description": "זיכוי על שירות שלא סופק",
      "quantity": "1",
      "unit_price": "-300",
      "vat_rate": "18",
      "note": "הזיכוי מתייחס למסמך המקורי לפי הסכם השירות."
    }
  ]
}
```

## Workflow 5: Explain a subscription or retainer

Use for monthly services.

1. Add `service_period` in `DD/MM/YYYY-DD/MM/YYYY`.
2. Keep the description specific.
3. Use one line per service bundle when the accounting system supports it.
4. Include the period in the explanation.
5. Confirm the period matches the invoice date and contract.

## Workflow 6: Review explanations before sending

1. Check document type and business type.
2. Check each amount against the accounting system.
3. Check VAT wording.
4. Remove unnecessary internal codes from descriptions.
5. Confirm Hebrew terminology is natural.
6. Keep the final explanation with the final document version.

## Workflow 7: Add a high-value B2B allocation-number caution

Use when the document is a business-to-business חשבונית מס and the amount before VAT is above the validated Israel Invoice threshold. In 2026, the threshold is ₪10,000 before VAT from 01/01/2026 and ₪5,000 before VAT from 01/06/2026.

1. Explain the line item normally.
2. Do not claim that an allocation number was issued unless the source document supplies it.
3. Add a short caution: "For high-value B2B tax invoices, verify whether an Israel Invoice allocation number is required."
4. If the customer asks about input VAT, recommend verifying the allocation number and the customer status before deducting input VAT.
5. Keep the wording practical and avoid legal conclusions.

Example note:

> Because this is a high-value B2B tax invoice, verify whether an Israel Invoice allocation number is required and visible on the source document.
