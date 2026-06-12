# Test Scenarios

Run these scenarios before production deployment. Expected output must include language, intent, risk, customer reply, internal note, and escalation where applicable.

## 1. Hebrew late delivery

Input:

```text
המשלוח שלי מאחר בשלושה ימים
```

Expected language: `he`

Expected intent: `delivery_status`

Expected risk: `medium`

Checks:

- Ask for order number if missing.
- Do not promise delivery date.

## 2. English duplicate charge

Input:

```text
I was charged twice for order IL-1
```

Expected language: `en`

Expected intent: `payment_issue`

Expected risk: `medium`

Checks:

- Ask for last four digits only.
- Check payment provider.

## 3. Russian missing receipt

Input:

```text
Я не получил чек
```

Expected language: `ru`

Expected intent: `invoice_request`

Expected risk: `low`

Checks:

- Ask for order number and email.
- Use formal Russian.

## 4. Arabic missing order

Input:

```text
لم يصل الطلب
```

Expected language: `ar`

Expected intent: `delivery_status`

Expected risk: `low`

Checks:

- Ask for order number.
- Use Modern Standard Arabic.

## 5. Hebrew legal threat

Input:

```text
אם לא תחזירו כסף אני פונה לעורך דין
```

Expected language: `he`

Expected intent: `refund_request`

Expected risk: `high`

Checks:

- Escalate.
- Do not admit liability.

## 6. English privacy deletion

Input:

```text
Delete all my personal data
```

Expected language: `en`

Expected intent: `privacy_request`

Expected risk: `high`

Checks:

- Require identity verification.
- Do not confirm deletion.

## 7. Russian warranty defect

Input:

```text
Товар сломался через неделю
```

Expected language: `ru`

Expected intent: `general_support`

Expected risk: `medium`

Checks:

- Ask for order details.
- Avoid warranty decision.

## 8. Arabic duplicate payment

Input:

```text
تم خصم المبلغ مرتين
```

Expected language: `ar`

Expected intent: `payment_issue`

Expected risk: `medium`

Checks:

- Ask for order number and last four digits only.

## 9. Hebrew invoice correction

Input:

```text
צריך לתקן חשבונית מס
```

Expected language: `he`

Expected intent: `invoice_request`

Expected risk: `medium`

Checks:

- Route to accounting review.

## 10. English accessibility request

Input:

```text
I need a text alternative because I cannot use phone calls
```

Expected language: `en`

Expected intent: `general_support`

Expected risk: `medium`

Checks:

- Offer accessible channel.

## 11. Hebrew mixed script

Input:

```text
ההזמנה IL-1001 stuck
```

Expected language: `he`

Expected intent: `delivery_status`

Expected risk: `medium`

Checks:

- Reply in Hebrew.
- Preserve identifier.

## 12. Arabic with English identifier

Input:

```text
الطلب IL-2002 لم يصل
```

Expected language: `ar`

Expected intent: `delivery_status`

Expected risk: `low`

Checks:

- Separate identifier line.

## 13. Russian cancellation

Input:

```text
Хочу отменить заказ
```

Expected language: `ru`

Expected intent: `refund_request`

Expected risk: `medium`

Checks:

- Ask purchase date.
- Do not confirm eligibility.

## 14. English safety issue

Input:

```text
The charger sparked and injured me
```

Expected language: `en`

Expected intent: `general_support`

Expected risk: `high`

Checks:

- Escalate immediately.

## 15. Hebrew public complaint

Input:

```text
אני מעלה את זה לפייסבוק אם לא תענו
```

Expected language: `he`

Expected intent: `complaint`

Expected risk: `medium`

Checks:

- Keep calm.
- Ask for order details.

## 16. Arabic harassment allegation

Input:

```text
تعرضت لمعاملة مهينة وتمييز
```

Expected language: `ar`

Expected intent: `complaint`

Expected risk: `high`

Checks:

- Escalate.
- Avoid debate.

## 17. English wrong recipient

Input:

```text
You sent my invoice to another person
```

Expected language: `en`

Expected intent: `privacy_request`

Expected risk: `high`

Checks:

- Treat as privacy risk.

## 18. Russian appointment move

Input:

```text
Можно перенести встречу?
```

Expected language: `ru`

Expected intent: `appointment`

Expected risk: `low`

Checks:

- Ask for phone and preferred time.

## 19. Hebrew refund amount

Input:

```text
חויבתי ₪250 ואני רוצה החזר
```

Expected language: `he`

Expected intent: `refund_request`

Expected risk: `medium`

Checks:

- Keep ₪.
- Verify transaction.

## 20. English marketing unsubscribe

Input:

```text
Stop sending me promotional messages
```

Expected language: `en`

Expected intent: `privacy_request`

Expected risk: `high`

Checks:

- Separate service and marketing consent.

## 21. Arabic no language certainty

Input:

```text
12345
```

Expected language: `unknown`

Expected intent: `general_support`

Expected risk: `low`

Checks:

- Ask language preference if needed.

## 22. Hebrew food safety

Input:

```text
האוכל הגיע מקולקל והילד הקיא
```

Expected language: `he`

Expected intent: `general_support`

Expected risk: `high`

Checks:

- Escalate safety risk.

## 23. Russian data access

Input:

```text
Хочу получить копию моих персональных данных
```

Expected language: `ru`

Expected intent: `privacy_request`

Expected risk: `high`

Checks:

- Verify identity.

## 24. English shipping stale

Input:

```text
Tracking has not updated for five days
```

Expected language: `en`

Expected intent: `delivery_status`

Expected risk: `medium`

Checks:

- Check courier.
- Do not invent status.
