# Troubleshooting

Use this reference when the estimate, courier bill, or customs result differs from expectations.

## Estimate lower than actual bill

Likely causes:

- Freight or insurance was omitted.
- Courier included service fees, storage, security, or handling.
- Exchange rate differed from the estimate.
- VAT was charged on a broader base.
- Purchase tax applied.
- Customs changed the classification.
- Customs rejected the declared value.
- The shipment included extra items, samples, or gifts.

Actions:

1. Request the customs entry, tax breakdown, and courier invoice.
2. Compare tariff code, customs value, exchange rate, and tax base.
3. Separate government taxes from courier/broker fees.
4. Recalculate with actual values.
5. Document differences for future shipments.

## Courier asks for ID, invoice, or payment proof

Reason: Customs clearance requires importer identity, transaction value, and product details.

Actions:

- Provide invoice or order confirmation.
- Provide proof of payment.
- Provide product page or technical datasheet.
- Provide ID or business registration details.
- Do not alter values to match desired tax outcome.

## Shipment held for standard approval

Reason: Product may be subject to an official standard or import legality condition.

Actions:

1. Identify exact product and model.
2. Check whether the standard applies to personal or commercial import.
3. Contact the courier or broker for the required approval path.
4. Provide test reports, declarations, or lab approval if available.
5. Do not ship regulated products commercially before checking requirements.

## Wireless device held

Reason: Devices with Wi‑Fi, Bluetooth, cellular, radio, or other transmitters may require communications review.

Actions:

- Provide model number, datasheet, frequencies, power output, and CE/FCC documents if available.
- Check personal-import exemptions separately from commercial import rules.
- Confirm whether the product is prohibited, exempt, or approval-required.

## Purchase tax appears unexpectedly

Reason: The product's tariff line carries purchase tax or a special formula.

Actions:

1. Verify the Israeli tariff code.
2. Check the purchase tax line and calculation base.
3. Confirm whether the product is complete, part, accessory, or kit.
4. Ask for broker review when the tax is material.

## Supplier HS code does not match Israeli code

Reason: Supplier invoices often show export HS codes or only 6-digit international HS headings.

Actions:

- Use supplier HS as a clue only.
- Validate Israeli tariff suffix and local taxes.
- Compare description, material, use, and technical specs.
- Record alternative classifications.

## Value challenged by customs

Reason: Declared value may appear too low, related-party pricing may be questioned, or freight may be missing.

Actions:

- Provide proof of payment.
- Provide order confirmation.
- Provide marketplace listing.
- Provide contract or proforma invoice.
- Provide explanation for discount, warranty replacement, used condition, or sample treatment.

## Returned goods treated as new import

Reason: Missing proof that the goods were previously exported from Israel for repair/replacement.

Actions:

- Provide export shipment record.
- Provide RMA or repair authorization.
- Provide repair invoice.
- Provide original purchase/import documents.
- Ask the broker whether outward-processing or returned-goods treatment is available.

## VAT charged on duty-free product

Reason: Duty-free does not mean VAT-free. VAT often applies unless a specific exemption exists.

Actions:

- Recalculate VAT base.
- Check whether personal import relief applies.
- Verify the official VAT rate on the estimate date.

## Mixed shipment classified incorrectly

Reason: Courier or supplier used one generic description for multiple products.

Actions:

- Split by line item.
- Provide product-level descriptions.
- Allocate freight.
- Ask for corrected invoice if necessary.

## CLI calculation fails

| Message | Cause | Fix |
|---|---|---|
| `goods_value must be non-negative` | Negative amount supplied | Correct the input |
| `exchange_rate_to_ils must be positive` | Missing or zero exchange rate | Provide valid rate |
| `rate must be between 0 and 1` | Used `18` instead of `0.18` | Use decimal rate |
| `special duty formulas require manual calculation` | Specific duty field needed | Calculate manually or add custom fee |
| `mixed shipments require line items` | Multiple products passed as one | Use the JSON line-item workflow |

## Web validation mismatch

Likely causes:

- A temporary threshold expired.
- A source page was cached or outdated.
- The product has a special tariff formula.
- A browser-facing customs page changed structure.
- The helper used a supplied exchange rate instead of the official customs exchange rate.

Actions:

1. Check the same claim against two different official or official-adjacent sources.
2. Prefer the source with the later effective date and the competent authority.
3. Replace hard-coded thresholds with live-source validation.
4. Record the correction in `references/verification-log.md`.
