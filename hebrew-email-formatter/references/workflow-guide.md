# Workflow Guide

Use these workflows to produce consistent Hebrew email drafts from incomplete user requests.

## Workflow 1: First payment reminder

1. Select `purpose=payment_reminder`.
2. Use `formality=neutral`.
3. Include invoice number, invoice date, amount, due date, and payment terms.
4. Open softly with `רציתי לוודא`.
5. Request an update, not immediate escalation.
6. Close with a concise signature.

Example:

```text
שלום דנה,

רציתי לוודא שחשבונית 2026-041 מיום 01/05/2026 התקבלה אצלכם.

סכום לתשלום: 3,500 ₪
תאריך פירעון: 31/05/2026
תנאי תשלום: שוטף + 30

אשמח לקבל עדכון לגבי מועד התשלום הצפוי.

תודה,
יואב לוי
```

## Workflow 2: Firm payment reminder

1. Select `formality=firm`.
2. Mention prior reminder date only when supplied.
3. Use neutral grammar when recipient gender is unknown.
4. Include amount and due date.
5. Request update by a concrete date.
6. Avoid threats unless approved wording is supplied.

## Workflow 3: Quote for a new business client

1. Select `purpose=quote`.
2. Use `formal` for a procurement department or first contact.
3. List scope in bullets.
4. Include timeline, cost, VAT status, and validity date.
5. Use written approval wording.
6. Add tax details only when supplied.

## Workflow 4: Sending an invoice

1. Select `purpose=invoice_sent`.
2. State exact document type.
3. Mention attachment only when confirmed.
4. Include amount, terms, and due date.
5. Ask whether another detail is needed for payment processing.

## Workflow 5: Meeting request

1. Select `purpose=meeting_request`.
2. Offer two or three time windows.
3. Include medium and expected duration.
4. Request confirmation or an alternative date.

## Workflow 6: Consumer complaint

1. Select `purpose=consumer_complaint`.
2. Use `formal`.
3. State purchase or order facts.
4. Describe the problem in one precise sentence.
5. List order number, purchase date, amount, and requested remedy.
6. Request written response by a concrete date.
7. Avoid legal conclusions unless approved wording is supplied.

## Workflow 7: Complaint response for a small business

1. Thank the customer for raising the issue.
2. Confirm the request was received.
3. Avoid blame or defensive wording.
4. State who is checking the issue if known.
5. Give a written response date.

## Workflow 8: Apology for delivery delay

1. Acknowledge the delay.
2. Avoid long explanations unless supplied.
3. Give a new delivery date.
4. Offer an additional update when relevant.
5. Use sender gender only when the sentence requires it.

## Workflow 9: Cancellation notice

1. Identify service, order, or account.
2. State requested cancellation date.
3. Request written confirmation.
4. Ask about remaining balance or refund where relevant.
5. Do not quote legal rights unless supplied.

## Workflow 10: Project status update

1. Use sections: completed, planned, attention needed.
2. Include dates and approval needs.
3. Keep the tone factual and brief.
4. End with a clear request when approval is required.

## Quality gate

Before returning the final draft:

- Confirm the subject identifies the purpose.
- Confirm the Hebrew is natural and concise.
- Convert dates to `DD/MM/YYYY`.
- Confirm amounts use `₪`.
- Check VAT wording.
- Check gendered verbs.
- Remove unnecessary personal data.
- Keep review notes visible.
