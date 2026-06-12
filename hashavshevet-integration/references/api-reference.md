# API and regulation reference

Access date for all sources: 2026-06-05.

## Israeli VAT and business thresholds

| Item | Current value | Integration impact | Source |
|---|---:|---|---|
| Standard VAT rate | 18% from 01-01-2025 | Use `0.18` for current VAT calculations unless an invoice date requires a historical rate. | Israel Tax Authority glossary: https://www.gov.il/en/pages/taxes-glossary |
| VAT increase order | 17% to 18% from 01-01-2025 | Update import validations and invoice tests for 2025 onward. | Knesset notice: https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx |
| Exempt dealer ceiling 2026 | ₪122,833 | Flag expected annual turnover above the ceiling before classifying a business as עוסק פטור. | Online exempt-dealer opening service: https://www.gov.il/he/service/request-open-exempt-dealer-via-internet |
| Small business reform ceiling | About ₪122,833 in 2026 | Align small-business classification and reporting prompts. | Small business owner topic: https://www.gov.il/he/departments/topics/income-tax-small-business-owner-24 |

Short source quotes:

- Tax glossary: "18% starting from January 1, 2025"
- Exempt dealer service: "בשנת 2026 – 122,833 ₪"
- Knesset notice: "effective January 1, 2025"

## Israel Invoices allocation number

| Effective date | Net invoice threshold before VAT | Rule |
|---|---:|---|
| 05-05-2024 | ₪25,000 | Allocation-number mandate rollout begins for qualifying invoices. |
| 01-01-2025 | ₪20,000 | Input VAT deduction depends on allocation number above the threshold. |
| 01-01-2026 | ₪10,000 | Current rule for early 2026. |
| 01-06-2026 | ₪5,000 | Lower threshold applies from June 2026. |

Sources:

- Israel Invoice topic: https://www.gov.il/en/departments/topics/israel-invoice/govil-landing-page
- Allocation-number application service: https://www.gov.il/en/service/request-assignment-number-for-tax-invoice
- Supplier invoice verification service: https://www.gov.il/en/service/verify-vendor-invoice-information

Short source quotes:

- Israel Invoice topic: "NIS 20,000 threshold set for 2025"
- Verification service: "10,000 starting January 1, 2026 and 5,000 NIS starting June 1, 2026"
- Application service: "Invoice amount before VAT; VAT amount"

### Required allocation request data

Include these fields before any SHAAM allocation workflow:

| Field | Validation |
|---|---|
| `customer_vat_number` | 9 digits; identify an authorized dealer/customer. |
| `invoice_number` | Non-empty and unique in the issuing company. |
| `invoice_date` | Valid date; evaluate threshold by date. |
| `net_amount` | Amount before VAT; compare to current threshold. |
| `vat_amount` | Use 18% for current standard VAT unless a special VAT rule applies. |
| `document_type` | Tax invoice or tax invoice/receipt for allocation checks. |

## SHAAM Open API paths

Use the Tax Authority developer portal and product subscription flow for actual credentials. Keep sandbox and production base URLs separate.

| Purpose | Known path or family | Notes | Source |
|---|---|---|---|
| OAuth authorization | `/shaam/tsandbox/longtimetoken/oauth2/authorize` | Browser authorization-code step in sandbox. | Tax Authority Open API PDF: https://www.gov.il/BlobFolder/service/connect-to-shaam/he/Service_Pages_shaam_Tax-Authority-Open-API.pdf |
| OAuth token | `/shaam/tsandbox/longtimetoken/oauth2/token` | Exchange authorization code for token in sandbox. | Tax Authority Open API PDF: https://www.gov.il/BlobFolder/service/connect-to-shaam/he/Service_Pages_shaam_Tax-Authority-Open-API.pdf |
| Invoice approval sandbox | `/shaam/tsandbox/Invoices/v1/Approval` | Request allocation approval for invoice data. | Israel Invoice API description: https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/IncomeTax_software-houses-en-040723.pdf |
| Production invoice family | `/shaam/production/Invoices/v1/` | Subscribe and verify exact endpoint in portal before production use. | SHAAM production connectivity references: https://www.gov.il/he/service/connect-to-shaam |
| Supplier invoice information | `/shaam/production/invoice-information/v1/` | Verify incoming supplier invoice details by allocation number where enabled. | Supplier invoice verification service: https://www.gov.il/en/service/verify-vendor-invoice-information |

Short source quotes:

- API description: "https://openapi.taxes.gov.il/shaam/tsandbox/Invoices/v1/Approval"
- Open API PDF: "longtimetoken/oauth2/token"
- Connect to SHAAM: "connect to the Shaam Computer"

### SHAAM error table

| Error or status | Likely cause | Action |
|---|---|---|
| `invalid_client` | Wrong client ID, secret, product subscription, or environment | Verify portal application, sandbox/production base URL, and product subscription. |
| `invalid_grant` | Expired or reused authorization code | Repeat the authorization-code flow and submit the new code once. |
| `401 Unauthorized` | Missing or expired bearer token | Refresh token and retry once with idempotency control. |
| `403 Forbidden` | User lacks delegated permission for the company | Recreate authorization through an eligible company user. |
| `400 Bad Request` | Missing customer number, invoice number, net amount, or VAT amount | Validate payload locally and log rejected field names. |
| Allocation denied | Tax Authority rule or risk check rejected the invoice | Follow official alternatives and keep accountant approval with the invoice. |
| `429 Too Many Requests` | Rate limit or repeated retries | Back off, preserve queue order, and avoid duplicate invoice submissions. |
| `5xx` | Tax Authority service or network failure | Queue the invoice, retry with backoff, and document downtime handling. |

## Hashavshevet and WizCloud integration references

| Area | Reference | Integration notes |
|---|---|---|
| WizCloud API documentation | https://docs.wizcloud.co.il/ | Supports import of journal transactions, items, documents, and data export through reports. |
| Hashavshevet cloud API help | https://home.wizcloud.co.il/help/apidocument/ | Requires an authorization token created by a super user for API access. |
| Hashavshevet documented import interfaces | https://www.h-erp.co.il/%D7%AA%D7%9E%D7%99%D7%9B%D7%94-%D7%91%D7%91%D7%AA%D7%99-%D7%AA%D7%95%D7%9B%D7%A0%D7%94/documentation-english/ | Documents journal, bank statement, item, and document import formats. |
| Account card import | https://www.h-erp.co.il/%D7%AA%D7%9E%D7%99%D7%9B%D7%94-%D7%91%D7%91%D7%AA%D7%99-%D7%AA%D7%95%D7%9B%D7%A0%D7%94/heshin/ | Use `HESHIN.DAT` and `HESHIN.PRM` for account-card import workflows. |

Short source quotes:

- WizCloud docs: "Import journal transactions, item records, documents"
- Cloud API help: "אסימון הרשאה"
- Import docs: "The value of the Quantity field should not be 0"

### Hashavshevet import error table

| Symptom | Likely cause | Action |
|---|---|---|
| Account rejected | Missing Account ID or unknown account | Load customer/supplier master data first or use an approved auto-open process. |
| Quantity rejected | Quantity is zero in a document import | Reject row and request a corrected quantity. |
| Combined invoice/receipt rejected | Target interface does not support combined document import | Split invoice and receipt into separate imports. |
| Wrong VAT posting | Incorrect transaction type or VAT account mapping | Validate transaction-type rules and account defaults per company. |
| Bank statement continuity error | Cumulative balance does not continue from existing statement | Rebuild the file from the last accepted bank line. |
| Duplicate document | Existing document number in the company | Stop import and reconcile numbering source. |
| Hebrew text corrupted | Wrong encoding | Convert Windows-1255 input to UTF-8 during staging, then write target encoding as required. |

## OPENFORMAT/BKMV

| File | Purpose |
|---|---|
| `INI.TXT` | Summary and generation metadata. |
| `BKMVDATA.TXT` | Business/accounting records such as accounts, journal entries, documents, items, and summary records. |

Official reference: https://www.gov.il/BlobFolder/service/registration-software-designed-managing-computerized-accounting-system/he/Service_Pages_Income_tax_horaot-131.pdf

Short source quote:

- OPENFORMAT instructions: "INI.TXT" and "BKMVDATA.TXT"

### OPENFORMAT validation table

| Error | Cause | Action |
|---|---|---|
| Missing `INI.TXT` | Incomplete export bundle | Regenerate from accounting software. |
| Missing `BKMVDATA.TXT` | Incomplete export bundle | Regenerate from accounting software. |
| Count mismatch | Summary totals do not match data records | Re-export and compare by record type. |
| Unsupported record type | Parser does not recognize a record | Update parser schema or exclude from non-official staging. |
| Invalid encoding | File opened with the wrong code page | Convert only in staging and keep the original export unchanged. |
