# Migration Checklist

Use this checklist when moving from manual document issuance or another invoicing provider to a Green Invoice (Morning) API integration.

## 1. Discovery

| Task | Output |
|---|---|
| Identify legal entity and business type | עוסק מורשה, חברה בע״מ, עוסק פטור, עמותה, or other account type. |
| Identify all document types currently issued | Quote, order, delivery note, tax invoice, tax invoice-receipt, receipt, credit note, deposits, purchase orders. |
| Identify VAT treatments | Taxable, exempt, mixed, foreign-currency export, reverse-charge or special cases. |
| Identify payment channels | Cash, check, card, bank transfer, PayPal, Bit, PayBox, withholding tax. |
| Identify external systems | E-commerce, CRM, ERP, payment gateway, bookkeeping export, data warehouse. |
| Identify reporting deadlines | Monthly VAT, income tax advances, withholding certificates, donation reporting. |

## 2. Data mapping

| Source field | Green Invoice field | Notes |
|---|---|---|
| Customer legal name | `client.name` | Use legal name for B2B customers. |
| Customer email | `client.emails[]` | Use accounting email for B2B. |
| Israeli עוסק or ח.פ. | `client.taxId` | Required for robust B2B allocation workflows. |
| Country | `client.country` | Use `IL` for Israeli clients. |
| SKU | `income[].catalogNum` or `itemId` | Prefer catalog item for recurring products. |
| Line description | `income[].description` | Should be clear on the issued document. |
| Quantity | `income[].quantity` | Preserve source precision when needed. |
| Unit price | `income[].price` | Store whether price includes VAT in source mapping. |
| Currency | `currency`, `income[].currency`, `payment[].currency` | Do not mix currency assumptions. |
| Exchange rate | `currencyRate` | Freeze rate when accounting requires it. |
| Tax treatment | `vatType`, `income[].vatType`, `income[].vatRate` | Validate with accountant before production. |
| Payment method | `payment[].type` | Map source payment channels to API enum. |
| Source order id | `remarks` or external database mapping | Used for idempotency and reconciliation. |

## 3. Numbering and historical data

- Do not import old document numbers as new official numbers.
- Preserve historical documents in the previous system or archive exports as required by record-retention rules.
- Start API-created documents only after the account numbering series is configured.
- Store a crosswalk table: `source_system`, `source_id`, `green_invoice_document_id`, `green_invoice_number`, `environment`, `created_at`.
- For open invoices migrated from another system, decide whether to record only future receipts in Green Invoice or keep settlement in the old system.

## 4. Client migration

1. Export active clients from the previous system.
2. Normalize emails, phone numbers, country codes, and tax ids.
3. Deduplicate clients by tax id first, then email, then normalized name.
4. Create clients in sandbox and review search/update behavior.
5. Create clients in production only after field mapping is approved.
6. Keep old customer id in `accountingKey` or in the source-system crosswalk.

## 5. Catalog migration

1. Export products and services.
2. Split catalog items by VAT treatment, currency, and revenue account when needed.
3. Avoid a single generic item for every sale; it weakens reporting.
4. Mark obsolete items inactive rather than reusing them for different products.
5. Test item search and document creation using catalog references.

## 6. Payment migration

| Previous payment channel | Payment type |
|---|---:|
| Cash | 1 |
| Check | 2 |
| Credit card | 3 |
| Bank transfer | 4 |
| PayPal | 5 |
| Bit or PayBox | 10 |
| Withholding tax | 0 |
| Other | 11 |

For withholding tax, record the actual money movement and the withheld amount as separate payment rows. Example: invoice total ₪11,800, bank transfer ₪11,210, withholding tax ₪590.

## 7. SHAAM allocation readiness

- Identify B2B flows that create `305` or `320`.
- Confirm customer tax id is mandatory in those flows.
- Complete Tax Authority authorization in the dashboard.
- Add runtime checks for high-value taxable B2B invoices.
- Store `taxAuthorityAllocationNumber` or the equivalent allocation field returned by the account.
- Define a manual stop procedure when allocation is missing.

## 8. Sandbox migration rehearsal

- Run the 20+ scenarios in `test-scenarios.md`.
- Create representative documents for each source-system order type.
- Compare document PDFs/downloads to accountant-approved examples.
- Test retry and duplicate-prevention behavior.
- Test webhook verification and event replay.
- Confirm all generated examples are clearly marked as sandbox data.

## 9. Production rollout

| Phase | Action | Rollback |
|---|---|---|
| Pilot | Enable API issuance for one low-risk flow | Return that flow to manual issuance. |
| B2C rollout | Enable low-value immediate payment documents | Disable automation and continue manual issuing. |
| B2B rollout | Enable business customers with valid `taxId` | Block high-value invoices until allocation verified. |
| Webhooks | Enable event processing after signature verification | Process documents by periodic search until fixed. |
| Full automation | Enable all approved flows | Pause queue consumers and use manual dashboard issuance. |

## 10. Post-migration controls

- Daily reconciliation between source orders and issued document ids.
- Alert on failed document creation and unknown timeout outcomes.
- Alert on duplicate source order ids mapped to multiple document ids.
- Alert on B2B tax invoices above threshold without allocation number.
- Monthly review of credit notes and cancellations.
- Periodic secret rotation.
- Periodic webhook secret rotation and replay tests.
- Quarterly review of VAT and withholding mappings with accounting owner.

## 11. Cutover checklist

- Production API key created and stored.
- Sandbox API key removed from production environment.
- Source order id mapping deployed.
- Retry policy deployed.
- Webhook signature verification deployed.
- Operator dashboard shows failed, pending, and issued states.
- Accountant approved sample documents.
- Customer support has explanation templates for invoice, receipt, and credit note questions.
- Manual fallback procedure tested.
