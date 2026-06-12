# Workflow Guide

Use these workflows to implement, migrate, audit, and release RTL interfaces for Hebrew and Arabic users.

## Workflow 1: New Hebrew landing page

Goal: publish a service landing page with a contact form, phone link, price display, and booking action.

1. Set the document boundary.

```html
<html lang="he" dir="rtl">
```

2. Use logical layout.

```css
.hero {
  padding-inline: 1rem;
  padding-block: 3rem;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
```

3. Keep phone and email LTR.

```html
<a href="tel:+972501234567" dir="ltr">050-123-4567</a>
<a href="mailto:info@example.co.il" dir="ltr">info@example.co.il</a>
```

4. Make form fields direction-specific.

```html
<input name="fullName" dir="auto" autocomplete="name" />
<input name="phone" type="tel" dir="ltr" inputmode="tel" autocomplete="tel" />
<textarea name="message" dir="auto"></textarea>
```

5. Display price safely.

```html
<p>מחיר החל מ-<bdi dir="ltr">₪ 250</bdi></p>
```

6. Test Hebrew, Arabic, English, phone numbers, long service text, and narrow screens.

## Workflow 2: React checkout

Goal: create a checkout with totals, delivery date, contact details, coupon, and payment action.

1. Derive direction from locale once.
2. Apply direction at the route or application shell.
3. Isolate product names, SKUs, order numbers, coupons, amounts, dates, and emails.
4. Format ILS with `Intl.NumberFormat`.
5. Keep payment iframes isolated if the embedded provider is LTR.
6. Test negative discounts, Arabic names, English product names, Hebrew delivery addresses, and keyboard order.

## Workflow 3: Tailwind dashboard migration

1. Search for physical classes.

```bash
grep -R "ml-\|mr-\|pl-\|pr-\|left-\|right-\|text-left\|text-right\|space-x-" src
```

2. Convert by semantic intent.

| Intent | Before | After |
|---|---|---|
| leading padding | `pl-4` | `ps-4` |
| trailing action | `right-2` | `end-2` |
| paragraph alignment | `text-right` | `text-start` |
| adjacent spacing | `space-x-2` | `gap-2` |
| leading border | `border-r-4` in an RTL-only design | `border-s-4` |

3. Avoid mechanical replacements.
4. Add visual and behavior tests for Hebrew, Arabic, and English.
5. Use `rtl:` and `ltr:` variants only for real exceptions.

## Workflow 4: Existing LTR product adding Hebrew

1. Add locale and direction to routing.
2. Add translation keys.
3. Move visible strings out of components.
4. Replace physical CSS with logical CSS.
5. Replace physical Tailwind utilities.
6. Add `dir="auto"` to user-generated values.
7. Keep technical identifiers LTR.
8. Review charts and data visualizations.
9. Review icon mirroring semantics.
10. Test keyboard and screen-reader behavior.
11. Add visual regression snapshots for English and Hebrew.
12. Release behind a feature flag when possible.

## Workflow 5: Invoice or receipt view

1. Use document-level RTL.

```html
<section lang="he" dir="rtl" class="invoice">
```

2. Isolate identifiers.

```html
<p>מספר מסמך: <bdi dir="ltr">INV-2026-0042</bdi></p>
```

3. Use DD/MM/YYYY.

```html
<p>תאריך: <bdi dir="ltr">03/06/2026</bdi></p>
```

4. Keep entity numbers LTR.

```html
<p>מספר עוסק: <bdi dir="ltr">512345678</bdi></p>
```

5. Align table values semantically.

```css
.invoice-table th,
.invoice-table td {
  text-align: start;
}

.invoice-table .amount {
  text-align: end;
  direction: ltr;
  unicode-bidi: isolate;
}
```

6. Test browser view, print view, PDF, and email attachment.

## Workflow 6: Arabic alongside Hebrew

1. Use `lang="ar"` and `dir="rtl"` for Arabic.
2. Use Arabic translations rather than Hebrew labels.
3. Test Arabic shaping.
4. Avoid Hebrew-specific abbreviations in shared components.
5. Keep phone, email, URL, amount, ID, and SKU direction LTR.
6. Confirm fonts cover Hebrew, Arabic, Latin, punctuation, and ₪.
7. Test mixed Hebrew-Arabic branch names with `dir="auto"`.

## Workflow 7: QA handoff

Provide:
- Build URL.
- Locale switch instructions.
- Test accounts.
- Hebrew, Arabic, English, and mixed text samples.
- Sample order, invoice, refund, appointment, and support ticket.
- Expected screenshot baseline for LTR if available.

Ask QA to record page, locale, direction, browser, device, text sample, expected behavior, actual behavior, keyboard step, and screenshot.

## Workflow 8: Production rollout

1. Freeze translations before final QA.
2. Run static scans for physical CSS and Tailwind utilities.
3. Run automated tests.
4. Run manual RTL scenarios.
5. Verify analytics payloads do not depend on visible text order.
6. Verify emails and PDFs.
7. Verify monitoring includes locale and direction.
8. Roll out gradually.
9. Compare conversion, error rate, and support contacts by locale.
10. Keep rollback path.
