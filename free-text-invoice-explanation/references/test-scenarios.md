# Test Scenarios

Use these scenarios to validate explanations before production use.

| ID | Scenario | Input focus | Expected behavior |
| --- | --- | --- | --- |
| 01 | Standard consulting invoice | Authorized dealer, tax invoice, 18% VAT | Show subtotal, VAT, and total. |
| 02 | Monthly website maintenance | Service period present | Mention the service period. |
| 03 | Exempt dealer receipt | Exempt dealer, receipt, 0% VAT | Explain no VAT added and receipt confirms payment. |
| 04 | Receipt with VAT rate | Receipt, VAT rate 18 | Warn not to present receipt as tax invoice. |
| 05 | Credit note | Credit note, negative amount | Explain reduction and link to original document. |
| 06 | Reimbursed courier fee | `reimbursable` true | Explain pass-through cost and request support. |
| 07 | Reverse charge service | `reverse_charge` true | Zero VAT and caution customer to verify obligation. |
| 08 | VAT-exempt line | `exempt_from_vat` true | Zero VAT and explain based on supplied data. |
| 09 | Missing description | Empty description | Produce validation error. |
| 10 | Quantity zero | Quantity 0 | Produce validation error. |
| 11 | Negative price outside credit note | Negative amount, ordinary invoice | Produce warning. |
| 12 | Invalid VAT rate | VAT rate above 100 | Produce validation error. |
| 13 | Foreign currency | USD currency | Show USD amount without inventing exchange rate. |
| 14 | Uncommon currency | JPY currency | Produce informational warning. |
| 15 | Mixed VAT rates | Multiple lines with different rates | Explain each line separately. |
| 16 | Consumer-facing explanation | Customer type consumer | Keep wording simple and avoid accounting assumptions. |
| 17 | Accountant-facing explanation | Customer type accountant | Include exact issue flags and fields. |
| 18 | Detailed caveat | Detailed output and caveat true | Include verification caveat. |
| 19 | Short output | Short detail level | Avoid long warning explanations. |
| 20 | Hebrew localization | Hebrew output | Use `₪`, `DD/MM/YYYY`, and Israeli terms. |
| 21 | English localization with ILS | English output, ILS currency | Use `₪` and clear VAT wording. |
| 22 | Invoice-receipt | Document type invoice-receipt | Explain charge and payment context when supplied. |
| 23 | Proforma | Document type proforma | Avoid final tax wording. |
| 24 | Discount line | Discount description and negative amount | Prefer credit-note warning unless same-document discount is explicit. |
| 25 | Subscription bundle | Quantity 1, service period | Explain recurring coverage. |
| 26 | Multiple quantities | Quantity above 1 | Explain quantity and unit price. |
| 27 | Business name supplied | Context includes business name | Keep name available without changing amounts. |
| 28 | Note supplied | Line note present | Include client note. |
| 29 | CLI file input | JSON input file | Print valid JSON with explanations. |
| 30 | CLI output file | Output path supplied | Write JSON to file. |
| 31 | Async client | Async methods | Return the same calculations as sync methods. |
| 32 | Payload from JSON string | JSON string input | Parse and explain. |
| 33 | Missing lines array | No `lines` key | Raise schema error. |
| 34 | Date conversion | ISO input date | Display `DD/MM/YYYY` when requested. |
| 35 | No amount breakdown | Option disabled | Omit subtotal and VAT breakdown text. |

## Acceptance criteria

A scenario passes when:

1. The output is valid JSON where JSON is expected.
2. Amounts are rounded to two decimals.
3. Hebrew output has no unnecessary English accounting terms.
4. The explanation avoids legal or tax guarantees.
5. Validation issues are explicit and actionable.

| 37 | Allocation-number caution | B2B tax invoice above 2026 threshold | Add a cautious note without inventing a number. |
| 38 | VAT default source check | Authorized dealer, standard VAT example | Use 18% as configurable default and preserve validation caveat. |
