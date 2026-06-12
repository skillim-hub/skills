# Israeli API and Regulation Reference

This reference covers Israeli systems, laws, and public data sources that commonly affect catalogs, VAT, prices, inventory exports, and invoicing workflows. It is an implementation reference, not legal or tax advice. Verify current rules and endpoints against official sources before live use.

Validation status: web-validated on 02/06/2026. See `references/verification-log.md` for source snippets, URLs, and second-pass checks.

## Source map

| Area | Official or practical source | Catalog impact |
|---|---|---|
| VAT and tax invoices | Israel Tax Authority | Store VAT rate per item and preserve historical rates. |
| Invoice allocation | Israel Tax Authority “חשבוניות ישראל” | Covered tax invoices above the current threshold may need an allocation number. |
| Consumer price display | Consumer Protection and Fair Trade Authority | Consumer-facing prices generally need clear final prices where applicable. |
| Currency | Bank of Israel and Israel Tax Authority customs currency service | Supplier costs in foreign currency need a documented conversion policy. |
| Computerized bookkeeping software | Israel Tax Authority software registry guidance | Accounting, inventory, or document-production systems may require valid registration. |
| Companies and dealers | Israeli registrars and tax identifiers | Supplier and customer IDs belong in parties, not SKU. |
| Barcodes | GS1/GTIN conventions | Barcode differs from internal SKU. |
| Customs/import | Israel Tax Authority customs systems | Imported goods may require classification, landed cost, warranty, and serial tracking. |

## Current validated constants for 2026

| Constant | Validated value | Source note |
|---|---:|---|
| Standard VAT rate | `0.18` | Israel Tax Authority and Knesset sources confirm 18% from 01/01/2025. |
| Invoice Israel threshold, 2025 | ₪20,000 before VAT | Tax Authority publication for businesses. |
| Invoice Israel threshold, 01/01/2026 to 31/05/2026 | ₪10,000 before VAT | Tax Authority publication for businesses. |
| Invoice Israel threshold, from 01/06/2026 | ₪5,000 before VAT | Tax Authority publication for businesses and second-pass professional summaries. |
| Bank of Israel series API host | `https://edge.boi.gov.il` | Bank of Israel API guide, 2026. |
| Older Bank of Israel public exchange-rate endpoint | `Boi.org.il/PublicApi/GetExchangeRates?asXml=true` | Bank of Israel migration guidance; prefer current series API for new builds. |

Do not hard-code future VAT changes or future invoice thresholds without revalidation. Keep `vat_rate` on each item and on every issued document so historical records remain correct after statutory changes.

## Israel Tax Authority: VAT line data

Recommended catalog payload for an accounting connector:

```json
{
  "sku": "COF-BNS-001",
  "description": "פולי קפה 1 ק״ג",
  "quantity": "2",
  "unit": "kg",
  "unit_price_before_vat": "42.37",
  "vat_rate": "0.18",
  "line_total_before_vat": "84.74",
  "line_vat": "15.25",
  "line_total_with_vat": "99.99",
  "currency": "ILS"
}
```

Example response from a connector:

```json
{
  "status": "accepted",
  "document_id": "INV-2026-000123",
  "warnings": [
    {
      "code": "ROUNDING_DIFFERENCE",
      "message": "Line rounding differs from document rounding by 0.01."
    }
  ]
}
```

### VAT error table

| Code | Meaning | Catalog remediation |
|---|---|---|
| `VAT_RATE_REQUIRED` | VAT rate missing. | Fill `vat_rate` on every SKU. |
| `INVALID_VAT_RATE` | Wrong format or unsupported value. | Store decimal rates such as `0.18`; convert only during export if target expects percent. |
| `EXEMPT_DEALER_VAT_CONFLICT` | VAT charged when business configuration says exempt. | Confirm business status and document type. |
| `ROUNDING_DIFFERENCE` | Totals differ by rounding. | Apply consistent decimal rounding policy. |
| `DESCRIPTION_TOO_LONG` | Item description exceeds target limit. | Add shorter `invoice_description`. |
| `DOCUMENT_DATE_OUT_OF_RANGE` | Date invalid for reporting. | Use actual issue date and preserve historical prices. |
| `NEGATIVE_LINE_PRICE` | Credit/refund loaded as normal item price. | Use credit/refund document workflow. |

## “חשבוניות ישראל” invoice allocation

Invoice allocation workflows can require approved allocation numbers for covered tax invoices. The validated public threshold schedule is ₪20,000 before VAT in 2025, ₪10,000 before VAT from 01/01/2026, and ₪5,000 before VAT from 01/06/2026. Authentication, endpoint paths, and exact payload field names are integration-specific and can change; treat the following as a neutral connector shape, not an official endpoint contract.

Example allocation request shape:

```json
{
  "dealer_number": "512345678",
  "document_type": "tax_invoice",
  "document_number": "2026-000123",
  "issue_date": "2026-06-02",
  "customer": {
    "name": "לקוח בע״מ",
    "tax_id": "515555555"
  },
  "totals": {
    "amount_before_vat": "1000.00",
    "vat_amount": "180.00",
    "amount_with_vat": "1180.00"
  },
  "lines": [
    {
      "line_number": 1,
      "sku": "SRV-SETUP-001",
      "description": "הקמת מערכת",
      "quantity": "1",
      "unit": "project",
      "unit_price_before_vat": "1000.00",
      "vat_rate": "0.18"
    }
  ]
}
```

Example allocation response shape:

```json
{
  "request_id": "9f3c2b5c-4a9b-4e23-a0dd-2c1cbd000001",
  "status": "approved",
  "allocation_number": "987654321",
  "valid_until": "2026-06-02T23:59:59+03:00"
}
```

### Allocation error table

| Code | Meaning | Remediation |
|---|---|---|
| `AUTH_REQUIRED` | Token missing or expired. | Refresh credentials in the accounting integration. |
| `DEALER_NOT_AUTHORIZED` | Business lacks permission. | Check digital authorization and Tax Authority registration. |
| `INVALID_CUSTOMER_TAX_ID` | Customer identifier invalid. | Fix customer record. |
| `AMOUNT_THRESHOLD_NOT_MET` | Allocation not required for the current threshold. | Continue ordinary invoice flow if allowed. |
| `AMOUNT_MISMATCH` | Totals do not match lines. | Recalculate from decimal source values. |
| `DUPLICATE_DOCUMENT_NUMBER` | Document already submitted. | Reconcile document sequence before retry. |
| `TEMPORARY_UNAVAILABLE` | Service unavailable. | Retry with backoff; avoid duplicate invoices. |

## VAT configuration record

Keep default rates outside item rows and keep historical rates on documents.

```json
{
  "country": "IL",
  "currency": "ILS",
  "default_vat_rate": "0.18",
  "default_vat_rate_source": "Israel Tax Authority",
  "verified_on": "2026-06-02",
  "notes": "Standard VAT rate confirmed as 18% for 2026 on official and second-pass sources. Reverify before production changes."
}
```

Rate-change procedure:

1. Confirm official effective date.
2. Freeze issued invoices.
3. Update default rate for new items.
4. Decide whether to preserve final consumer prices or before-VAT prices.
5. Recalculate future price lists.
6. Keep old rates on historical quotes and invoices as required.
7. Test old-rate and new-rate scenarios.

## Consumer price display

Consumer exports should favor final prices. The Consumer Protection and Fair Trade Authority explains price display rules, and enforcement materials identify non-VAT-inclusive displays as a violation risk.

Consumer export example:

```csv
sku,name_he,unit,price_with_vat,currency,updated_at,notes
MUG-WHT-001,ספל לבן,unit,25.00,ILS,02/06/2026,מחיר כולל מע״מ
```

B2B export example:

```csv
sku,name_he,unit,price_before_vat,vat_rate,price_with_vat,currency,updated_at
MUG-WHT-001,ספל לבן,unit,21.19,0.18,25.00,ILS,02/06/2026
```

### Price-display error table

| Code | Meaning | Fix |
|---|---|---|
| `PRICE_NOT_FINAL` | Consumer file lacks final price. | Include `price_with_vat` and currency. |
| `VAT_LABEL_MISSING` | Before-VAT price not labeled. | Add `vat_rate` and clear note. |
| `STALE_PRICE_LIST` | No update date. | Add `updated_at` and effective date. |
| `MIXED_AUDIENCE` | Same export used for consumers and B2B. | Produce separate exports. |

## Bank of Israel exchange-rate reference

Imported goods and foreign supplier costs may require exchange-rate records. For new integrations, use the Bank of Israel series API guide. The current documented host is `edge.boi.gov.il` with SDMX paths under `/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/...`. Older exchange-rate guidance also mentions `Boi.org.il/PublicApi/GetExchangeRates?asXml=true`; treat older paths as migration references, not the default for a new build.

Request shape based on the 2026 Bank of Israel series API guide:

```http
GET https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/?c%5BBASE_CURRENCY%5D=USD&c%5BCOUNTER_CURRENCY%5D=ILS&format=csv
Accept: text/csv
```

Response shape after normalizing a published observation:

```json
{
  "currency": "USD",
  "counter_currency": "ILS",
  "date": "2026-06-02",
  "rate_to_ils": "3.7000",
  "source": "Bank of Israel representative exchange rates"
}
```

Costing example:

```json
{
  "sku": "ACC-CBL-001",
  "supplier_currency": "USD",
  "supplier_unit_cost": "4.80",
  "exchange_rate_to_ils": "3.7000",
  "landed_cost_ils": "17.76",
  "selling_price_before_vat_ils": "39.90"
}
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| `RATE_NOT_PUBLISHED` | Rate unavailable for date. | Use approved fallback policy. |
| `CURRENCY_UNSUPPORTED` | Currency not available. | Validate ISO currency code. |
| `COST_PRICE_CONFUSION` | Cost exported to customers. | Separate internal costing and public price lists. |

## Israel Tax Authority customs currency service

For customs/import workflows, the Tax Authority provides a currency-rate query service for customs purposes. Keep this separate from retail price-list exchange-rate policy.

```json
{
  "use_case": "customs_import_costing",
  "source": "Israel Tax Authority currency-rate query service",
  "fields_to_store": ["currency", "rate_date", "rate", "customs_reference"]
}
```

## Barcodes and GTIN

Internal SKU, supplier SKU, and barcode are separate identifiers.

```json
{
  "sku": "MUG-WHT-001",
  "supplier_sku": "SUP-9981",
  "barcode": "7290000000000",
  "barcode_type": "EAN13",
  "validation_status": "format_valid_unverified_owner"
}
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| `BARCODE_NOT_NUMERIC` | Invalid characters. | Keep digits only. |
| `BARCODE_LENGTH_INVALID` | Unsupported length. | Confirm EAN/UPC/GTIN format. |
| `BARCODE_OWNER_UNVERIFIED` | Ownership not checked. | Verify with supplier or barcode authority. |
| `SKU_BARCODE_CONFLICT` | Same barcode mapped to multiple active SKUs. | Review variants and bundles manually. |

## Company, dealer, and supplier identifiers

Keep identifiers in party records, not SKUs.

```json
{
  "supplier_name": "ספק לדוגמה בע״מ",
  "company_number": "515555555",
  "vat_dealer_number": "515555555",
  "contact_email": "orders@example.co.il",
  "supplier_sku_prefix": "SUP"
}
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| `IDENTIFIER_IN_SKU` | Company or dealer number embedded in SKU. | Move identifier to supplier/customer record. |
| `SUPPLIER_MISSING` | Purchase lacks supplier. | Add supplier before purchase import. |
| `ID_FORMAT_INVALID` | Basic format invalid. | Verify against official source or supplier document. |

## Import and customs fields

Imported goods may need optional fields.

```json
{
  "sku": "ELEC-ADP-001",
  "country_of_origin": "CN",
  "hs_code": "850440",
  "importer_name": "Importer Ltd",
  "serial_tracking": true,
  "warranty_months": 12,
  "landed_cost_ils": "28.40"
}
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| `HS_CODE_MISSING` | Imported item lacks classification. | Add `hs_code` where required. |
| `SERIAL_REQUIRED` | Serial tracking needed. | Enable serial workflow. |
| `WARRANTY_MISSING` | Warranty details missing. | Add warranty fields and customer notes. |

## Webhooks

No official public webhook event-name contract was confirmed for the catalog use case during the 02/06/2026 validation pass. Do not document or implement webhook event names unless the connected accounting or tax vendor provides its own contract.

## Export profiles

| Profile | Include | Exclude |
|---|---|---|
| Consumer price list | SKU, name, unit, price with VAT, notes | Supplier cost, supplier contact, margin |
| B2B price list | SKU, name, unit, price before VAT, VAT rate, price with VAT | Supplier cost, internal notes |
| Accounting import | SKU, description, unit, price before VAT, VAT rate | Marketing text |
| Stock count sheet | SKU, name, shelf/bin, expected quantity | Supplier prices and customer prices |
| Supplier reorder | Supplier SKU, supplier name, quantity to order | Customer price and margin |

## Integration readiness checklist

- [ ] VAT rate stored per item.
- [ ] Price before VAT stored as decimal string.
- [ ] Price including VAT calculated consistently.
- [ ] SKU unique across active and inactive items.
- [ ] Hebrew stored in UTF-8.
- [ ] Barcode stored separately.
- [ ] Supplier SKU stored separately.
- [ ] Services marked zero-stock or non-stock.
- [ ] Stock movements include reason and reference.
- [ ] Consumer and B2B exports separated.
- [ ] Historical VAT rates preserved.
- [ ] Invoice Israel thresholds revalidated before live invoice allocation.
- [ ] Official API host and endpoint paths verified before production use.
