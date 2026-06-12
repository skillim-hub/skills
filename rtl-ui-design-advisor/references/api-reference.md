# API, Browser, Framework, Localization, and Regulation Reference

This package is not an external API client. Treat this file as an implementation reference for browser APIs, framework patterns, localization data, static audit output, and Israeli regulatory checkpoints that affect interface design.

Confirm current official legal, tax, accessibility, and privacy requirements before release sign-off.

## HTML direction API

### `dir`

```html
<html lang="he" dir="rtl">
<span dir="auto">Maya Cohen</span>
<bdi dir="ltr">INV-2026-0042</bdi>
```

| Value | Meaning | Use |
|---|---|---|
| `rtl` | Right-to-left base direction | Hebrew or Arabic page or section |
| `ltr` | Left-to-right base direction | Email, URL, phone, code, ID, amount, embedded English |
| `auto` | Browser infers from first strong character | User names, business names, comments, search |

Error table:

| Code | Meaning | Fix |
|---|---|---|
| `HTML_DIR_MISSING` | Root element has no direction | Set `dir` from locale |
| `FORM_LTR_DIR_MISSING` | LTR field inherits RTL | Set `dir="ltr"` |
| `BIDI_DYNAMIC_VALUE_REVIEW` | Mixed inline value may be unisolated | Use `<bdi>` or `dir` on the value |

### `lang`

```html
<html lang="he" dir="rtl">
<p lang="ar" dir="rtl">مرحبا</p>
<code lang="en" dir="ltr">npm run build</code>
```

Recommended tags:

| Tag | Use |
|---|---|
| `he` | Hebrew |
| `he-IL` | Hebrew localized for Israel |
| `ar` | Arabic |
| `ar-IL` | Arabic localized for Israel |
| `en` | English |
| `en-IL` | English localized for Israel |

## CSS logical properties

```css
.panel {
  margin-inline-start: 1rem;
  padding-inline: 1rem;
  border-inline-end: 1px solid #ddd;
  inset-inline-start: 0;
}
```

| Physical | Logical replacement |
|---|---|
| `margin-left` | `margin-inline-start` or `margin-inline-end` after semantic review |
| `margin-right` | `margin-inline-end` or `margin-inline-start` after semantic review |
| `padding-left` | `padding-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-left` | `border-inline-start` |
| `border-right` | `border-inline-end` |
| `left` | `inset-inline-start` |
| `right` | `inset-inline-end` |
| `text-align: left` | `text-align: start` or `text-align: end` by meaning |
| `text-align: right` | `text-align: start` for default RTL paragraphs |

## JavaScript `Intl.NumberFormat`

Request:

```ts
const formatter = new Intl.NumberFormat("he-IL", {
  style: "currency",
  currency: "ILS",
  currencyDisplay: "symbol"
});
formatter.format(1250);
```

Display pattern in RTL text:

```html
<p>סה"כ לתשלום: <bdi dir="ltr">₪ 1,250.00</bdi></p>
```

Error table:

| Error | Cause | Fix |
|---|---|---|
| Currency symbol moves | Missing isolation | Wrap the formatted result with `<bdi>` |
| Decimal separators vary | Manual formatting | Use `Intl.NumberFormat` |
| VAT total mismatch | UI hard-coded business value | Calculate in shared business logic or server layer |

## JavaScript `Intl.DateTimeFormat`

Use a clear Israeli policy. For many business flows, display DD/MM/YYYY.

```ts
function formatIsraelDate(date: Date) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  }).formatToParts(date);
  const get = (type: string) => parts.find((part) => part.type === type)?.value ?? "";
  return `${get("day")}/${get("month")}/${get("year")}`;
}
```

Response example:

```txt
03/06/2026
```

## React API pattern

```ts
const rtlLocales = new Set(["he", "he-IL", "ar", "ar-IL"]);

export function getDir(locale: string): "rtl" | "ltr" {
  return rtlLocales.has(locale) ? "rtl" : "ltr";
}
```

Request-like input:

```json
{ "locale": "he-IL" }
```

Response:

```json
{ "dir": "rtl" }
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| `LOCALE_DIR_MISSING` | Locale exists but direction is not derived | Use one helper |
| `PORTAL_DIR_LOST` | Dialog, popover, or tooltip renders outside RTL tree | Add `dir` to portal root |
| `HYDRATION_DIR_MISMATCH` | Server and client render different directions | Derive from the same locale source |

## Tailwind reference

| Intent | Utility |
|---|---|
| margin inline start | `ms-*` |
| margin inline end | `me-*` |
| padding inline start | `ps-*` |
| padding inline end | `pe-*` |
| inset inline start | `start-*` |
| inset inline end | `end-*` |
| text start | `text-start` |
| text end | `text-end` |
| border inline start | `border-s` |
| border inline end | `border-e` |

Request:

```txt
flex ml-4 text-left left-0
```

Response:

```json
{
  "summary": { "total": 3, "high": 0, "medium": 3, "low": 0 },
  "issues": [
    {
      "severity": "medium",
      "code": "TW_PHYSICAL_MARGIN",
      "message": "Physical Tailwind utility detected: ml-4",
      "recommendation": "Use ms-* or me-* after semantic review.",
      "line": null,
      "evidence": "ml-4"
    }
  ]
}
```

## Static audit storage schema

`create_audit` returns an audit record and stores it under `.rtl-advisor-audits` unless a different store directory is provided.

```json
{
  "id": "audit_20260603_120000_abcdef12",
  "kind": "tailwind",
  "env": "sandbox",
  "created_at": "2026-06-03T12:00:00Z",
  "result": {
    "summary": { "total": 1, "high": 0, "medium": 1, "low": 0 },
    "issues": []
  }
}
```

## Israeli localization data patterns

### Verified standard VAT rate

Live web validation on 03/06/2026 double-confirmed that the Israeli standard VAT rate is 18%, effective 01/01/2025. Use this as documentation context only. Keep the actual rate in configuration, the server, or accounting logic rather than in presentational UI components.

```json
{
  "jurisdiction": "IL",
  "tax": "VAT",
  "standardRate": 0.18,
  "effectiveFrom": "2025-01-01",
  "displayExample": "₪ 180.00 on ₪ 1,000.00 subtotal",
  "source": "references/verification-log.md"
}
```


### Phone

```json
{
  "display": "050-123-4567",
  "e164": "+972501234567",
  "href": "tel:+972501234567",
  "dir": "ltr"
}
```

Markup:

```html
<a href="tel:+972501234567" dir="ltr">050-123-4567</a>
```

### Business identifiers

Use LTR direction for תעודת זהות, ח"פ, מספר עמותה, מספר עוסק, ספק, חשבון בנק, סניף ומק"ט.

```html
<label for="business-id">מספר עוסק</label>
<input id="business-id" name="businessId" inputmode="numeric" dir="ltr" />
```

### Invoice and receipt labels

| Hebrew | English meaning | UI note |
|---|---|---|
| חשבונית מס | Tax invoice | Tax document context |
| קבלה | Receipt | Payment confirmation |
| חשבונית מס/קבלה | Tax invoice/receipt | Combined document |
| עוסק פטור | Exempt dealer | Do not assume VAT collection |
| עוסק מורשה | Authorized dealer | VAT may be relevant |
| ח"פ | Company number | Company context |
| מע"מ | VAT | Do not hard-code rate in UI |
| סה"כ לפני מע"מ | Total before VAT | Display amount isolated |
| סה"כ לתשלום | Total due | Display amount isolated |

Payload example:

```json
{
  "documentType": "tax_invoice_receipt",
  "documentNumber": "INV-2026-0042",
  "issueDate": "03/06/2026",
  "customerName": "דנה לוי",
  "subtotalIls": 1000,
  "vatIls": 180,
  "totalIls": 1180
}
```

Markup example:

```html
<section dir="rtl" lang="he">
  <h1>חשבונית מס/קבלה</h1>
  <p>מספר מסמך: <bdi dir="ltr">INV-2026-0042</bdi></p>
  <p>תאריך: <bdi dir="ltr">03/06/2026</bdi></p>
  <p>לקוח: <bdi dir="auto">דנה לוי</bdi></p>
  <p>סה"כ לתשלום: <bdi dir="ltr">₪ 1,180.00</bdi></p>
</section>
```

## Israeli regulatory checkpoints

### Accessibility

Relevant source areas include Israeli accessibility regulations and the Israeli standard aligned with WCAG principles. Treat this as an engineering checklist and verify final obligations with current official material.

| Area | UI implementation |
|---|---|
| Language | Accurate `lang` |
| Direction | Accurate `dir` |
| Keyboard | Logical focus order |
| Labels | Programmatic label association |
| Errors | `aria-describedby` and clear localized text |
| Zoom | Layout remains readable at high zoom |
| Dynamic updates | Announced in the correct language |

### Privacy

Relevant source area: Israeli privacy law and related data-protection obligations. UI forms, consent text, account screens, and data request flows must be clear in Hebrew or Arabic and must not expose unnecessary personal data in errors. Database registration, notice duties, and DPO duties are context-dependent under current privacy-law changes, so avoid hard-coded blanket claims in product UI.

### Consumer protection and e-commerce

Relevant source area: Israeli consumer protection obligations. Price, total cost, delivery terms, cancellation terms, business identity, and support contact details must remain readable and visible in RTL layouts.

### Tax and bookkeeping

Relevant source areas include Israeli tax authority rules and bookkeeping instructions. Preserve document numbers, dates, VAT labels, entity labels, and totals exactly. Keep tax rates and business rules out of presentational components.
