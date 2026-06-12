# Troubleshooting

## Language detection problems

| Symptom | Diagnosis | Fix |
|---|---|---|
| Short Hebrew message classified as Arabic | Sparse text or mixed-script identifiers | Use conversation history and ask for language preference if uncertain. |
| Russian customer gets English answer | Default language override | Store language per conversation and prefer latest customer language. |
| Arabic reply mixes dialects | Template set contains inconsistent sources | Standardize default Arabic to Modern Standard Arabic. |
| Product name translated incorrectly | Translation overreaches | Lock brand names, model names, SKUs, addresses, and person names. |

## RTL and LTR rendering

Use short sentences, isolate placeholders, and preview in the target channel.

Preferred Hebrew layout:

```text
מספר הזמנה: {{order_id}}
סטטוס: {{status}}
תאריך עדכון: {{date}}
```

Preferred Arabic layout:

```text
رقم الطلب: {{order_id}}
الحالة: {{status}}
تاريخ التحديث: {{date}}
```

Avoid long mixed-script sentences with multiple placeholders.

## Refund and cancellation mistakes

| Problem | Fix |
|---|---|
| Reply confirms refund before verification | Replace with review wording tied to transaction details and policy. |
| Reply ignores purchase date | Ask for purchase date in DD/MM/YYYY format. |
| Reply ignores product condition | Ask whether the product was opened, used, defective, or not received, only if relevant. |
| Reply promises processing time without payment-provider data | Use a verified provider status or neutral follow-up wording. |

## Payment safety

Never ask for a full card number, CVV, or password. If the customer sends such data, redact it from internal notes and continue with safe instructions.

Safe wording:

```text
Send only the order number and the last four digits of the payment method. Do not send the full card number.
```

## Accounting uncertainty

Use operational wording only:

```text
The document can be issued according to the purchase data in the accounting system. VAT classification or document correction requires accountant review.
```

## Privacy risk

Never repeat sensitive identifiers in the reply. Keep internal notes minimal.

```text
Customer requested deletion. Identity verification pending. Do not include identity number in ticket note.
```

## Escalation triggers

- Attorney, lawsuit, or formal legal notice.
- Chargeback or payment dispute.
- Injury, food safety, electrical safety, medicine, cosmetics, or child-related product issue.
- Data breach, wrong recipient, access request, correction request, or deletion request.
- Discrimination or harassment allegation.
- Customer threatens self-harm or violence.
- Public complaint with media, regulator, or viral-risk language.
- Accounting correction with tax impact.

## Common operational failures

| Failure | Root cause | Prevention |
|---|---|---|
| Wrong date format | Imported US template | Use DD/MM/YYYY in all customer-facing examples. |
| Wrong currency | Amount shown without symbol | Use ₪ for shekels; do not convert currency without a verified source. |
| Overcollection | Agent asks for unnecessary identity data | Map required fields per intent and channel. |
| Template drift | Local edits bypass review | Run the test scenarios after every template change. |
| Inconsistent escalation | High-risk terms not listed | Review real tickets and update risk terms monthly. |

## Recovery templates

### Wrong language

```text
Apologies for the language mismatch. The request can be handled in Hebrew, English, Russian, or Arabic. Reply with the preferred language and the support process will continue in that language.
```

### Premature refund promise

```text
Correction: the request must first be checked against the transaction details and business policy. After verification, the available options will be explained.
```

### Unsafe payment request

```text
Do not send full payment-card details. Send only the order number and the last four digits of the payment method.
```

### Unavailable system

```text
The system needed to verify the request is temporarily unavailable. The case will be checked again, and the next update will be sent after verification.
```
