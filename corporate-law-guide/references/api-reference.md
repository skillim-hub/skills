# Israeli Corporate-Law Reference

## Status

This reference maps legal sources and regulator-style workflows used by the skill. It is not a live API specification. Treat official legislation, Companies Authority publications, official forms, and professional advice as controlling.

## Sources to cite in answers

| Source | Hebrew | Use | Note |
|---|---|---|---|
| Companies Law, 5759-1999 | חוק החברות, התשנ״ט-1999 | Formation, organs, director duties, shareholder approvals, transactions, liquidation concepts | Check current consolidated text before section-specific reliance |
| Companies Regulations | תקנות החברות | Forms, registration details, reporting, fees, filing mechanics | Multiple regulations may apply |
| Corporations Authority / Companies Registrar | רשות התאגידים / רשם החברות | Incorporation, annual reports, changes, extracts, charges | Procedures and fees change |
| Partnerships Ordinance | פקודת השותפויות | Partnership alternative | Important for personal liability |
| Amutot Law | חוק העמותות | Non-profit alternative | Not for ordinary profit distributions |
| Securities Law | חוק ניירות ערך | Fundraising and investor solicitation | Escalate for offerings or crowdfunding |
| VAT Law and Income Tax Ordinance | חוק מע״מ ופקודת מס הכנסה | Tax coordination | Corporate registration does not open tax files |
| Prohibition on Money Laundering framework | דיני איסור הלבנת הון | Bank onboarding and beneficial ownership | Banks may demand ownership evidence |
| Consumer Protection Law | חוק הגנת הצרכן | Consumer terms, refunds, cancellation | Applies regardless of entity form |
| Protection of Privacy Law | חוק הגנת הפרטיות | Databases and customer data | Company registration does not solve privacy compliance |
| Employment law framework | דיני עבודה | Founder employment, contractors, options | Escalate for employee equity and classification |

## Workflow request model

Companies Authority procedures operate as filings rather than a public API for this skill. Model each as a structured request with inputs, attachments, validations, and possible rejection reasons.

### Incorporation request

```json
{
  "request_type": "incorporation",
  "names": {
    "hebrew_preferred": "דוגמה טכנולוגיות בע״מ",
    "hebrew_alternatives": ["דוגמה פתרונות בע״מ", "דוגמה מערכות בע״מ"],
    "english_preferred": "Example Technologies Ltd."
  },
  "registered_office": {"street": "הברזל", "house_number": "1", "city": "תל אביב-יפו", "postal_code": "6971001"},
  "share_capital": [{"class": "ordinary", "authorized_shares": 100000, "nominal_value": 0.01, "currency": "ILS"}],
  "initial_shareholders": [{"name": "Founder A", "id_type": "israeli_id", "id_number": "000000000", "shares": 50000, "class": "ordinary"}],
  "initial_directors": [{"name": "Founder A", "id_type": "israeli_id", "id_number": "000000000", "consent_attached": true}],
  "articles_attached": true,
  "declarations_attached": true
}
```

Expected response:

```json
{
  "status": "accepted",
  "company_number": "516000000",
  "certificate_issued": true,
  "next_steps": ["open_statutory_books", "approve_signing_rights", "open_bank_account", "coordinate_tax_registration"]
}
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| NAME_SIMILAR | Proposed name resembles existing name | Submit distinctive alternatives |
| NAME_RESTRICTED | Name includes protected/regulated term | Provide approval or change name |
| MISSING_ARTICLES | Articles missing or defective | Attach compliant articles |
| ID_MISMATCH | Identity details differ | Match IDs and names exactly |
| INVALID_SHARE_TOTAL | Issued shares exceed authorized capital | Reconcile share capital |
| MISSING_DECLARATION | Required declaration missing | Collect signed declaration |
| SIGNATURE_INVALID | Signature/authentication not accepted | Re-sign using accepted method |
| ADDRESS_INVALID | Registered office incomplete | Provide full Israeli address |

### Annual report request

```json
{
  "request_type": "annual_report",
  "company_number": "516000000",
  "report_year": 2026,
  "registered_office_confirmed": true,
  "directors": [{"name": "Director A", "id_number": "000000000", "appointment_date": "01/01/2026"}],
  "shareholders": [{"name": "Shareholder A", "shares": 50000, "class": "ordinary"}],
  "share_changes_during_year": false,
  "fee_paid": "verify_official_status"
}
```

Error table:

| Code | Meaning | Fix |
|---|---|---|
| COMPANY_NOT_FOUND | Number not found or mistyped | Check company extract |
| YEAR_ALREADY_FILED | Report already filed | Archive confirmation |
| MISSING_DIRECTOR_DATA | Director details incomplete | Update director list |
| SHAREHOLDER_MISMATCH | Shareholder data differs | Reconcile transfers/allotments |
| FEE_OUTSTANDING | Fee appears unpaid | Verify and pay if required |
| AUTH_REQUIRED | Submitter lacks authority | Use authorized submitter |

### Director update request

```json
{
  "request_type": "director_update",
  "company_number": "516000000",
  "effective_date": "15/03/2026",
  "action": "appoint",
  "director": {"name": "New Director", "id_type": "israeli_id", "id_number": "222222222", "consent_attached": true},
  "approval_document": "shareholder_resolution.pdf"
}
```

| Code | Meaning | Fix |
|---|---|---|
| CONSENT_MISSING | Director consent absent | Attach consent |
| DATE_INVALID | Date inconsistent | Use DD/MM/YYYY and confirm actual effective date |
| AUTHORITY_UNCLEAR | Appointment authority unclear | Provide correct resolution |
| PERSON_DETAILS_MISMATCH | Identity details inconsistent | Match ID/passport exactly |

### Share transfer request

```json
{
  "request_type": "share_transfer",
  "company_number": "516000000",
  "transfer_date": "20/04/2026",
  "seller": {"name": "Shareholder A", "id_number": "000000000"},
  "buyer": {"name": "Shareholder B", "id_number": "111111111"},
  "shares": {"class": "ordinary", "quantity": 1000},
  "approvals": {"board_approval": true, "rofr_waiver": true, "tax_review": "required_before_completion"},
  "documents": ["share_transfer_deed.pdf", "board_minutes.pdf", "deed_of_adherence.pdf"]
}
```

| Code | Meaning | Fix |
|---|---|---|
| TRANSFER_RESTRICTED | Articles/agreement restrict transfer | Obtain approval or waiver |
| SELLER_BALANCE_LOW | Seller lacks enough shares | Reconcile register |
| CLASS_MISMATCH | Share class differs | Check articles and registers |
| TAX_NOT_REVIEWED | Tax not addressed | Obtain tax advice |
| ADHERENCE_MISSING | New holder not bound | Sign deed of adherence |

### Charge registration request

```json
{
  "request_type": "charge_registration",
  "company_number": "516000000",
  "lender": "Bank Example Ltd.",
  "charge_type": "fixed_and_floating",
  "asset_description": "all assets, IP, receivables, and bank accounts",
  "creation_date": "01/05/2026",
  "documents": ["debenture.pdf", "board_approval.pdf"]
}
```

| Code | Meaning | Fix |
|---|---|---|
| LATE_REGISTRATION | Filing deadline may have passed | Escalate immediately |
| ASSET_DESCRIPTION_VAGUE | Assets unclear | Align with debenture |
| LENDER_DETAILS_INCOMPLETE | Secured party data missing | Complete exact legal details |
| DOCUMENT_MISMATCH | Filing and debenture differ | Reconcile before submission |

## Validation rules

- Store company number as a string, commonly nine digits.
- Use DD/MM/YYYY for Israeli-facing output.
- Use ₪ or ILS consistently.
- Match Hebrew names exactly across IDs, resolutions, filings, and bank forms.
- Name attachments as `YYYY-MM-DD_company-number_action_document-type_signed.pdf`.

## Professional-review triggers

Use review for conflicts between articles and agreements, minority objections, director conflicts, inability to pay debts, charges, foreign parties, options, warrants, SAFEs, convertible loans, consumer exposure, privacy exposure, and liquidation.


## Web-validated rate, threshold, fee, and API status reference

Validated on 02/06/2026:

| Item | Value or status | Notes |
|---|---|---|
| Standard VAT rate | 18% | Effective from 01/01/2025; verify before issuing invoices. |
| Company annual fee 2026 | ₪1,338 reduced until 31/03/2026; ₪1,777 from 01/04/2026 | Payment status can affect company compliance. |
| Partnership annual fee 2026 | ₪1,333 reduced until 31/03/2026; ₪1,771 from 01/04/2026 | Relevant when comparing company and partnership overhead. |
| Exempt dealer turnover threshold 2026 | ₪122,833 | Does not override occupation exclusions requiring licensed dealer status. |
| Developer API host | Not applicable | The skill models Companies Authority procedures as structured workflows, not public API calls. |
| Endpoint paths | Not applicable | Official channels are online services/forms such as gov.il and Corporations Online. |
| Webhook event names | Not applicable | No webhook-based integration is referenced or required. |

### Example validated facts payload

```json
{
  "validated_on": "02/06/2026",
  "vat_standard_rate": 0.18,
  "company_annual_fee_2026": {
    "reduced_until": "31/03/2026",
    "reduced_amount_ils": 1338,
    "regular_from": "01/04/2026",
    "regular_amount_ils": 1777
  },
  "partnership_annual_fee_2026": {
    "reduced_until": "31/03/2026",
    "reduced_amount_ils": 1333,
    "regular_from": "01/04/2026",
    "regular_amount_ils": 1771
  },
  "exempt_dealer_threshold_2026_ils": 122833,
  "public_api": false,
  "webhooks": []
}
```
