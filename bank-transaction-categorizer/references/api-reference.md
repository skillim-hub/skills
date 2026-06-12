# API and Regulatory Reference

## Web-validated source notes

Access date: 2026-06-02.

- Current general VAT rate: the Tax Authority VAT history states `1.1.25 עלה המע"מ ל-18%`, and the Tax Authority glossary states `18% החל מתאריך ה - 1.1.2025`.
- API hosts and endpoint paths in this document are illustrative adapter examples. The Bank of Israel standards page provides versioned ZIP specification packages rather than one universal production host.
- No webhook event names are implemented by this skill. Production work that uses Bank of Israel push-notification specifications must use the current BOI package and must not infer event names from these examples.
- Israeli open banking is consent-based. The Bank of Israel states that customers may share financial information with third parties with consent.
- Bank and acquirer names used in examples are examples of supervised entities listed by the Bank of Israel. Their appearance does not imply endorsement or integration.


This skill is file-first. It does not connect to bank APIs, does not request online banking credentials, and does not perform account aggregation. The references below document Israeli banking, privacy, and tax context for offline import and future consent-based integrations.

## Reference matrix

| Area | Israeli reference | Relevance | Status |
|---|---|---|---|
| Open banking | Bank of Israel open banking framework and Israeli Open Banking API standard | Consent-based account and transaction data access | Reference only |
| Bank statements | Exported CSV/Excel files from Israeli banks | Primary offline input | Supported by CSV-style import |
| Payment services | Israeli payment-services and payment-initiation regulation | Relevant to future API import | Reference only |
| Privacy | Protection of Privacy Law and Protection of Privacy Regulations (Data Security) | Bank statements contain sensitive personal and financial data | Apply local storage and access control |
| Bookkeeping | Israeli income-tax bookkeeping instructions and VAT documentation practice | Categorized output supports review | Draft output only |
| VAT | Israeli VAT documentation requirements | Determines whether invoice/receipt support may be needed | `vat_relevant` flag only |
| AML | Israeli banking and financial-services AML obligations | Relevant to regulated institutions | No AML decisioning |
| Consumer fees | Bank of Israel fee disclosure and fee schedules | Helps identify bank-fee lines | Rule recognition included |

Verify current requirements before filing, audit work, regulated integration, or customer-facing financial-product use.

## Future open-banking request examples

```http
GET /open-banking/v1/accounts HTTP/1.1
Host: api.example-bank.co.il  # illustrative only; use the current bank/BOI specification in production
Authorization: Bearer <access_token>
Accept: application/json
x-request-id: 0e8a2a66-7cc9-4939-a6c0-6f9bbd83d8fb
```

```json
{
  "data": {
    "accounts": [
      {
        "accountId": "acc_123",
        "bankCode": "12",
        "branchNumber": "678",
        "accountNumberMasked": "****4321",
        "currency": "ILS",
        "accountType": "current"
      }
    ]
  }
}
```

```http
GET /open-banking/v1/accounts/acc_123/transactions?fromDate=2026-01-01&toDate=2026-01-31 HTTP/1.1
Host: api.example-bank.co.il  # illustrative only; use the current bank/BOI specification in production
Authorization: Bearer <access_token>
Accept: application/json
x-request-id: 6988d50f-31ff-4b63-8ba6-6dbb22e230a0
```

```json
{
  "data": {
    "transactions": [
      {
        "transactionId": "txn_001",
        "bookingDate": "2026-01-02",
        "valueDate": "2026-01-02",
        "transactionInformation": "מע\"מ תקופתי",
        "amount": {"amount": "-1200.00", "currency": "ILS"},
        "creditDebitIndicator": "Debit",
        "balanceAfterTransaction": {"amount": "18450.20", "currency": "ILS"}
      }
    ]
  }
}
```

## Open-banking mapping

| API field | Internal field |
|---|---|
| `bookingDate` or `valueDate` | `date` |
| `transactionInformation` | `description` |
| `amount.amount` | `amount` |
| `amount.currency` | `currency` |
| `creditDebitIndicator` | `direction` |
| `transactionId` | `reference` |
| `balanceAfterTransaction.amount` | `balance` |
| institution identifier | `bank` |

## Error table for future connectors

| HTTP status | Meaning | Handling |
|---|---|---|
| 400 | Invalid request, date range, account id, or pagination token | Stop import and show validation details |
| 401 | Missing or expired token | Refresh token if allowed or renew consent |
| 403 | Consent does not cover requested account or scope | Revise consent or choose another account |
| 404 | Account or endpoint not found | Confirm account identifier and integration version |
| 409 | Consent or request-state conflict | Retrieve consent status and resume safely |
| 422 | Bank validation rule failed | Display field-level error |
| 429 | Rate limit exceeded | Back off and respect bank headers |
| 500 | Server error | Retry later and log request id |
| 503 | Service unavailable | Retry later; mark partial imports |

## Offline CSV request equivalent

```bash
python scripts/bank-transaction-categorizer-cli.py categorize statement.csv   --output categorized.csv   --rules custom-rules.json   --format csv
```

## Offline CSV response equivalent

```csv
date,description,amount,direction,category,subcategory,confidence,flags
2026-01-02,מע"מ תקופתי,-1200.00,debit,Taxes & Government,VAT,0.97,
2026-01-03,העברה מלקוח - חשבונית 1042,3500.00,credit,Income,Client payment,0.87,confirm-business-income
```

## CSV validation errors

| Code | Trigger | Fix |
|---|---|---|
| `missing-header` | No header row | Export with column names |
| `missing-date` | No date column or blank date | Add `תאריך`, `תאריך עסקה`, or `date` |
| `missing-description` | Missing transaction description | Add `תיאור`, `פרטים`, or `description` |
| `missing-amount` | No signed amount and no debit/credit pair | Add `סכום`, or `חובה` and `זכות` |
| `bad-date-format` | Unsupported date | Normalize to DD-MM-YYYY or YYYY-MM-DD |
| `bad-amount-format` | Unsupported amount text | Remove non-currency text |
| `empty-file` | No rows | Export a wider date range |

## Privacy handling

Process locally where possible. Keep raw statements in restricted folders. Remove full account numbers when sharing. Avoid storing credentials, one-time codes, or access tokens in statement folders. Keep custom rules private when they contain customer or supplier names. Encrypt backups containing statement data.
