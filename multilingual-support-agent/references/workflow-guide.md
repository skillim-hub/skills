# Workflow Guide

## Workflow 1: WhatsApp delivery-status request

1. Detect the customer language.
2. Extract order number, phone number, name, and tracking number if present.
3. If order number is missing, ask for it and do not guess.
4. Query the order system and courier system.
5. Convert the system status into customer-friendly wording.
6. Use DD/MM/YYYY for any date.
7. Log an internal note with intent, risk, missing fields, and source system status.

Hebrew customer reply:

```text
שלום {{customer_name}}, בדקנו את המשלוח להזמנה {{order_id}}.
סטטוס נוכחי: {{shipping_status_text}}
אם לא תהיה התקדמות עד {{date}}, נבדוק שוב מול חברת השליחויות.
```

Internal note:

```text
intent=delivery_status; risk=medium; order_id={{order_id}}; courier_status={{status}}; next_review={{date}}
```

## Workflow 2: Duplicate charge in English

1. Acknowledge the issue without confirming a duplicate before verification.
2. Ask for order number and last four payment digits only.
3. Check the payment provider for captured, voided, refunded, and pending transactions.
4. Check the order system for one or more order identifiers.
5. If a duplicate captured payment exists, route to the refund process.
6. If only an authorization hold exists, explain the distinction using provider-safe wording.

Customer reply:

```text
Hello, a duplicate charge will be checked against the transaction record and payment provider. Send the order number and only the last four digits of the payment method. Do not send the full card number.
```

## Workflow 3: Russian accounting document request

1. Identify the requested document: receipt, tax invoice, or tax invoice/receipt.
2. Verify that the purchase exists.
3. Ask for required business details if the customer needs a business document.
4. Send the request to the accounting system.
5. Escalate document corrections, VAT questions, and conflicting business details.

Customer reply:

```text
Здравствуйте, для подготовки бухгалтерского документа отправьте номер заказа и адрес электронной почты. Если нужен документ на компанию, отправьте название компании, регистрационный номер и адрес.
```

## Workflow 4: Arabic refund request

1. Confirm order number and purchase date.
2. Identify reason: change of mind, defect, late delivery, duplicate charge, or service complaint.
3. Request only necessary evidence.
4. Check business policy and applicable consumer-process requirements.
5. Do not promise an outcome before verification.
6. Escalate legal, safety, chargeback, or public complaint triggers.

Customer reply:

```text
مرحبًا، سيتم فحص طلب الاسترداد وفق تفاصيل الصفقة وتاريخ الشراء وسياسة العمل. يرجى إرسال رقم الطلب وتاريخ الشراء بصيغة DD/MM/YYYY.
```

## Workflow 5: Privacy deletion request

1. Treat the request as high risk.
2. Do not ask for unnecessary identifiers in the chat.
3. Verify identity through the approved process.
4. Identify systems that may contain personal data: CRM, ecommerce, accounting, email, messaging, marketing, support logs, courier exports.
5. Separate deletion, access, correction, objection, and unsubscribe requests.
6. Do not confirm completion until the procedure is complete.
7. Log status without repeating sensitive identifiers.

Holding reply:

```text
Hello, the privacy request was received. It requires identity verification and handling under the business procedure and applicable law. Send the email address linked to the request so the process can be started.
```

## Workflow 6: Appointment rescheduling

1. Detect whether the request is for a new appointment, cancellation, or reschedule.
2. Ask for phone number and preferred time windows.
3. Check the calendar or booking system.
4. Offer no more than two options.
5. Confirm timezone as Israel time when relevant.
6. Send a final confirmation after booking.

Hebrew reply:

```text
שלום, כדי לטפל בתור יש לשלוח מספר טלפון ושני מועדים נוחים. לאחר בדיקת הזמינות תישלח אפשרות לאישור.
```

## Workflow 7: Public complaint or review threat

1. Keep the reply calm.
2. Do not argue about facts in the public channel.
3. Move to a private channel only for personal details.
4. Ask for order number or contact details.
5. Escalate if the complaint mentions safety, discrimination, legal action, or media attention.

Customer reply:

```text
Thank you for explaining what happened. The case needs a full check against the order and service record. Send the order number and a short description of the issue so it can be reviewed.
```

## Workflow 8: Mixed-language message

1. Detect the dominant customer language.
2. Preserve product names, order identifiers, addresses, and quoted system statuses.
3. If no dominant language is clear, ask for preferred language.
4. Avoid mixing multiple languages in one sentence unless quoting the customer.

Example:

```text
ההזמנה IL-1001 stuck in transit
```

Reply in Hebrew and keep `IL-1001` unchanged.
