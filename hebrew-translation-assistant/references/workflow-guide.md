# Workflow guide

Use these workflows to produce practical Hebrew-English translations for Israeli small businesses, freelancers, and consumers.

## Workflow 1: Freelance invoice email

1. Identify direction and register: usually English to Hebrew, accounting-sensitive or business.
2. Preserve client name, amount, invoice number, due date, bank details, and VAT terms.
3. Use `חשבונית מס`, `חשבונית מס/קבלה`, `קבלה`, `מע״מ`, `העברה בנקאית`, and `אישור תשלום` according to the source.
4. Convert dates to `DD/MM/YYYY`.
5. Return a ready-to-send email and a short accounting note.

Example source:

```text
Please issue a tax invoice/receipt for ₪1,250 plus VAT by 2026-03-05.
```

Preferred Hebrew draft:

```text
נא להפיק חשבונית מס/קבלה על סך 1,250 ₪ בתוספת מע״מ עד 05/03/2026.
```

Checklist:

- Confirm whether the supplier is an `עוסק מורשה` or `עוסק פטור`.
- Confirm whether VAT is included or added.
- Confirm whether a receipt is required only after payment.

## Workflow 2: Consumer refund reply

1. Select support register.
2. Start with recognition of the issue.
3. State action and timing.
4. Preserve order number, amount, original payment method, and number of business days.
5. Avoid admitting liability unless the source does so.

Example source:

```text
Sorry for the delay. A refund will be issued within 7 business days.
```

Preferred Hebrew draft:

```text
מצטערים על העיכוב. ההחזר הכספי יבוצע בתוך 7 ימי עסקים.
```

## Workflow 3: E-commerce checkout localization

1. Translate UI labels concisely.
2. Keep product names and coupon codes unchanged.
3. Use Hebrew terms customers expect in Israel.
4. Test right-to-left rendering in the checkout flow.

| English UI | Hebrew UI |
|---|---|
| Add to cart | הוספה לסל |
| Checkout | תשלום |
| Order summary | סיכום הזמנה |
| Coupon code | קוד קופון |
| Payment method | אמצעי תשלום |
| Self pickup | איסוף עצמי |

## Workflow 4: Privacy notice translation

1. Select legal-sensitive register.
2. Preserve exact concepts: personal information, consent, service providers, data subject, retention, security.
3. Do not simplify consent beyond the source.
4. Flag the final text for professional privacy review.
5. Use `מדיניות פרטיות`, `מידע אישי`, `נושא מידע`, `הסכמה`, `ספקי שירות`, and `אבטחת מידע`.

Example note:

```text
Privacy-sensitive content: verify the final Hebrew wording against current privacy requirements before publication.
```

## Workflow 5: Lease or legal clause

1. Select legal-sensitive register.
2. Preserve defined terms and capitalized terms.
3. Do not translate a legal term into a broader everyday term.
4. Keep `הסכם שכירות`, `שטר חוב`, `ייפוי כוח`, `ערבות`, and `דמי ביטול` precise.
5. Add a review flag when legal effect is uncertain.

## Workflow 6: WhatsApp message to a client

1. Select casual register unless the matter is legal, accounting, or complaint-sensitive.
2. Keep the message short.
3. Avoid stiff phrasing.
4. Use neutral gender when unknown.

Example source:

```text
Can you send the payment confirmation today?
```

Preferred Hebrew:

```text
אפשר לשלוח היום את אישור התשלום?
```

## Workflow 7: Bilingual cleanup

1. Identify which terms should remain bilingual.
2. Keep product names, plan names, URLs, order IDs, and email addresses unchanged.
3. Fix Hebrew word order and punctuation.
4. Avoid unnecessary English when a real Hebrew term exists.
5. Check right-to-left punctuation at the end.

## Workflow 8: Stored CLI request

1. Install the package.
2. Set `HEBREW_TRANSLATION_ASSISTANT_HOME`.
3. Run `create` with `--env sandbox`.
4. Extract the returned `id`.
5. Run `show` with that id.
6. Review the translation and notes.
7. Run again with `--env production` only when the same workflow is intended for production records.

```bash
CREATE_RESPONSE="$(hebrew-translation-assistant create "Refund within 7 business days" --register support --env sandbox)"
REQUEST_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
hebrew-translation-assistant show "$REQUEST_ID"
```
