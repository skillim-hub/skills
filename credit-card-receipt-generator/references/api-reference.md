# API and Regulation Reference

Access date for all cited web sources: 2026-06-04.

## Validation summary

| Area | Current validated value | Primary URL |
|---|---|---|
| Israeli VAT rate | 18% from 01-01-2025 | https://www.gov.il/he/pages/vat-history |
| VAT interpretation notice | VAT increase from 17% to 18% for 2025 timing rules | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf |
| Osek Patur ceiling | ₪122,833 in 2026 | https://www.gov.il/he/service/request-open-exempt-dealer-via-internet |
| Israel Invoices threshold | ₪10,000 before VAT from 01-01-2026; ₪5,000 before VAT from 01-06-2026 | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice |
| Form 821 | VAT registration / authorized dealer application | https://www.gov.il/he/service/vat-821 |
| Form 5329 | Personal details and income sources report for opening an independent file | https://www.gov.il/he/service/itc5329 |
| Withholding and bookkeeping approvals | Check withholding tax and bookkeeping approvals | https://www.gov.il/he/service/itc-gmishurim |

## Short source excerpts

Each excerpt is kept under 140 characters.

- Israel Tax Authority VAT history: "1.1.25 עלה המע"מ ל-18%".
- Israel Tax Authority exempt dealer service: "בשנת 2026 – 122,833 ₪".
- Israel Tax Authority allocation service: "10,000 החל מה-1 בינואר 2026 ו-5,000 ₪ החל מה-1 ביוני 2026".
- Grow documentation: "Grow Payments (formerly Meshulam) Documentation Center".
- Tranzila documentation: "https://api.tranzila.com/v1/pr/create".
- Pelecard Postman collection: "https://gateway21.pelecard.biz/services/AddDebitTrxReceipt".

## Gateway endpoint map

Use these endpoint paths as integration references. Confirm merchant-specific permissions with each provider before production use.

| Gateway | Purpose | Method | Endpoint or base path | Notes |
|---|---|---:|---|---|
| Cardcom | Hosted payment page | POST | `https://secure.cardcom.solutions/api/v11/LowProfile/Create` | Hosted Low Profile flow; store `LowProfileId`. |
| Cardcom | Fetch hosted payment result | POST | `https://secure.cardcom.solutions/api/v11/LowProfile/GetLpResult` | Read transaction and document details. |
| Cardcom | Standalone document | POST | `https://secure.cardcom.solutions/api/v11/Documents/CreateDocument` | Requires document permissions and API password. |
| Tranzila | Payment request | POST | `https://api.tranzila.com/v1/pr/create` | Payment request creation. |
| Tranzila | Credit-card transaction | POST | `https://api.tranzila.com/v1/transaction/credit_card/create` | Server-side transaction API. |
| Tranzila | Iframe handshake | POST | `https://api.tranzila.com/v1/handshake/create` | Recommended before redirect/iframe entry. |
| Grow/Meshulam | Create payment process | POST | `https://sandbox.meshulam.co.il/api/light/server/1.0/createPaymentProcess` | Sandbox path from public docs; production credentials are merchant-specific. |
| Grow/Meshulam | Charge saved token | POST | `https://sandbox.meshulam.co.il/api/light/server/1.0/createTransactionWithToken` | Requires `transactionUniqueIdentifier` for idempotency in relevant flows. |
| Grow/Meshulam | Get payment link info | POST | `https://sandbox.meshulam.co.il/api/light/server/1.0/getPaymentLinkInfo` | Use for reconciliation. |
| Pelecard | Add receipt to debit transaction | POST | `https://gateway21.pelecard.biz/services/AddDebitTrxReceipt` | Public Pelecard Postman collection. |
| Pelecard | Debit regular transaction | POST | `https://gateway21.pelecard.biz/services/DebitRegularType` | Gateway21 REST path; send only from PCI-appropriate backend. |
| Pelecard | Pending regular transaction | POST | `https://gateway21.pelecard.biz/services/PendingRegularType` | Authorization/pending flow. |

## Normalized receipt fields

| Normalized field | Cardcom | Tranzila | Grow/Meshulam | Pelecard |
|---|---|---|---|---|
| success code | `ResponseCode == 0` | response status/code according to API response | `status`, `statusCode`, or documented success flag | `StatusCode == "000"` and successful `ShvaResult` |
| transaction ID | `TranzactionId` | `transaction_id`, `index`, or API transaction ID | `transactionId`, `transactionToken`, `paymentId` | `PelecardTransactionId` |
| approval reference | `ApprovalNumber` | `auth_number`, `confirmation_code` | `asmachta`, `authNumber` | `VoucherId`, `ConfirmationKey` |
| document number | `DocumentNumber`, `DocumentInfo.DocumentNumber` | provider invoice module field if enabled | invoice fields / `invoiceNotifyUrl` result | `AddDebitTrxReceipt` result if enabled |
| card display | `Last4`, masked card field | masked card or last4 | `cardSuffix`, masked card | `CreditCardNumber` only when masked |

## Error tables

### Normalized outcome table

| Category | Detection | Receipt action | Operator action |
|---|---|---|---|
| Success | Gateway success code plus transaction ID | Generate receipt draft | Reconcile against settlement report |
| Decline | Card/network/shva decline code | Do not issue paid receipt | Show neutral payment failure and allow retry |
| Validation error | Missing required field or wrong credential | Do not issue receipt | Correct request payload or credentials |
| Pending | Authorization, 3DS, pending, or delayed capture | Mark as pending only | Wait for capture/settlement event |
| Duplicate | Idempotency or duplicate transaction ID | Do not create a second receipt | Link to original receipt and verify amount |
| Document error | Payment succeeds but invoice/receipt creation fails | Generate payment record, not official document | Retry document generation or use accounting system |
| Security error | Raw PAN/CVV or token leakage detected | Stop output generation | Redact and rotate exposed secrets if needed |

### Provider-specific response checks

| Provider | Success indicator | Common failure indicators | Notes |
|---|---|---|---|
| Cardcom | Top-level `ResponseCode` is `0`; J2/J5 validation can return `700` or `701` as success-like validation states | Non-zero `ResponseCode`, nested `DocumentInfo.ResponseCode` failure | Check both HTTP status and JSON response code. |
| Tranzila | API success status and transaction ID returned by the v1 endpoint | Refused response, authentication error, 3DS not completed | Keep `X-tranzila-api-*` credentials server-side. |
| Grow/Meshulam | Successful payment process/token transaction status and transaction ID | Missing `userId`, invalid `pageCode`, duplicate `transactionUniqueIdentifier` | Use `notifyUrl` and `invoiceNotifyUrl` for reliable server notifications. |
| Pelecard | `StatusCode` `000` and successful `ShvaResult` in transaction response | Non-`000` status, rejected Shva result, pending transaction not finalized | Use Gateway21 or current provider collection when available. |

## Compliance notes

- Treat this package as a receipt draft and reconciliation helper. Use certified accounting software or provider document generation for official tax invoices and receipts.
- Keep full card data out of files. Store masked card display, last four digits, or gateway tokens only.
- For Osek Patur receipts, do not charge VAT and do not present a VAT component.
- For Osek Murshe or companies, display VAT when the transaction is VAT-chargeable.
- For B2B tax invoices above the Israel Invoices threshold, include the Tax Authority allocation number before treating the tax invoice as complete for input VAT deduction.
- Do not split transactions to avoid thresholds.

## Source list

- Israel Tax Authority VAT history: https://www.gov.il/he/pages/vat-history
- Israel Tax Authority VAT interpretation notice: https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf
- Exempt dealer online registration and 2026 ceiling: https://www.gov.il/he/service/request-open-exempt-dealer-via-internet
- Israel Invoices allocation number service: https://www.gov.il/he/service/request-assignment-number-for-tax-invoice
- Israel Invoices FAQ: https://www.gov.il/he/pages/faq_israel_invoice
- VAT Form 821 service: https://www.gov.il/he/service/vat-821
- Income Tax Form 5329 service: https://www.gov.il/he/service/itc5329
- Withholding and bookkeeping approvals: https://www.gov.il/he/service/itc-gmishurim
- Cardcom API V11: https://secure.cardcom.solutions/Api/v11/Docs
- Cardcom support article for Low Profile flow: https://cardcomapinametovalue.zendesk.com/hc/he/articles/27008964534162-Low-profile-interface-EN-Step-1-2
- Tranzila API docs: https://docs.tranzila.com/
- Tranzila payment request endpoint: https://docs.tranzila.com/docs/payments-billing/sszgfd8q7b8l0-payment-request
- Tranzila credit-card transaction endpoint: https://docs.tranzila.com/docs/payments-billing/wxeldbiapkj41-create
- Grow documentation center: https://grow-il.readme.io/
- Grow create payment process: https://grow-il.readme.io/reference/post_api-light-server-1-0-createpaymentprocess-9
- Grow token transaction: https://grow-il.readme.io/reference/post_api-light-server-1-0-createtransactionwithtoken-4
- Grow payment link info: https://grow-il.readme.io/reference/post_api-light-server-1-0-getpaymentlinkinfo-2
- Pelecard website API page: https://pelecard.com/api/
- Pelecard public Postman collection: https://www.postman.com/peleteam/pelecard-public/documentation/e8o62iu/gateway21
