# Workflow Guide

Use these end-to-end workflows to turn Tabu data into practical decisions for Israeli small businesses, freelancers, and consumers.

## Workflow 1: Consumer purchase due diligence

### Goal

Check whether the person selling a property appears to hold the rights being sold and whether registered restrictions require action before payment.

### Inputs

- Block, parcel, and subparcel.
- Seller name and masked ID.
- Draft sale agreement, if available.
- Mortgage bank or attorney details, if known.
- Fresh extract target date close to signing or payment.

### Steps

1. Normalize the parcel identifier.
2. Retrieve the current extract through the configured service.
3. Match seller name and ID against registered rights.
4. Check share. Confirm that the seller owns the share being sold.
5. Read encumbrances: mortgage, caveat, lien, attachment, lease, easement.
6. Create a risk flag for each registered restriction.
7. Compare apartment number with subparcel.
8. Prepare a concise summary for professional review.
9. Retrieve a fresh extract again before final payment or deed signing.

### Stop conditions

- Seller does not appear as owner or right holder.
- Registered share is smaller than the sale share.
- Attachment, lien, or unexplained caveat exists.
- Address and parcel mapping do not match.

## Workflow 2: Small business storefront lease check

### Goal

Check whether the landlord appears to have authority to lease the shop, office, clinic, workshop, warehouse, or studio.

### Inputs

- Full business premises address.
- Block, parcel, and subparcel from landlord, municipal bill, or contract.
- Landlord name and ID or company number.
- Lease term and options.
- Intended use: retail, clinic, food, office, manufacturing, or storage.

### Steps

1. Prefer block, parcel, and subparcel over address-only input.
2. Retrieve property record.
3. Confirm landlord or right-holder identity.
4. If a company owns the property, request signatory authority.
5. Check long lease, easements, mortgages, caveats, attachments, and restrictions.
6. Check whether the recorded property type and rights are consistent with the proposed lease.
7. Separate Tabu ownership facts from planning and business-licensing questions.
8. Flag missing business licensing or planning review.

### Stop conditions

- Landlord is not listed and no authority documents were provided.
- Property appears to be subject to a blocking attachment or receivership.
- Unit identification is unclear.

## Workflow 3: Freelancer home-office or studio purchase

### Goal

Check whether a residential or mixed-use unit has registered restrictions that may affect financing, use, or future sale.

### Steps

1. Retrieve exact subparcel.
2. Confirm owner and share.
3. Inspect encumbrances and easements.
4. Flag condominium bylaw or shared-property issues for separate review.
5. Check whether planning, business-use, VAT, or income-tax questions require separate review.
6. Produce a summary that separates ownership facts from tax and licensing implications.

## Workflow 4: Collateral check for a private loan or supplier credit

### Goal

Assess whether a property offered as collateral has visible registered restrictions.

### Steps

1. Normalize property identifier.
2. Retrieve extract.
3. Identify owner or right holder and share.
4. Check existing mortgages, charges, caveats, attachments, and liens.
5. If owner is a company, cross-check corporate charges through the appropriate process.
6. Estimate whether priority issues require professional review.
7. Do not accept collateral based only on a verbal statement.

### Stop conditions

- Owner mismatch.
- Existing mortgage or attachment without release or consent.
- Corporate ownership without signatory and charge review.

## Workflow 5: Inheritance or family transfer

### Goal

Clarify whether the registry reflects the current legal heirs or whether registration is still pending.

### Steps

1. Retrieve current extract.
2. Check whether the listed owner is deceased or whether an administrator is listed.
3. Request probate order, inheritance order, or court documents.
4. Verify that all heirs or authorized representatives match the proposed transaction.
5. Flag unresolved estate registration as a legal-review requirement.

### Stop conditions

- Deceased owner still appears without registered transfer.
- One heir proposes to sell all rights without authority.
- Court order or inheritance order is missing.

## Workflow 6: Address-only consumer check

### Goal

Convert an address into a likely parcel while avoiding false certainty.

### Steps

1. Ask for city, street, house number, entrance, and apartment or unit number.
2. Run address lookup through a configured source.
3. If multiple parcels match, request municipal bill, sale contract, previous extract, or seller confirmation.
4. Do not summarize ownership until the parcel is confirmed.
5. Once parcel is confirmed, run the parcel workflow.

### Required output language

Use:

```text
The address lookup produced a candidate parcel. Treat this as a candidate only until confirmed against official documents.
```

Do not use:

```text
This address is definitely the property.
```

## Workflow 7: Mortgage release monitoring

### Goal

Verify whether a mortgage or lien was removed after payoff or settlement.

### Steps

1. Retrieve previous extract.
2. Retrieve new extract.
3. Compare encumbrances by type, beneficiary, date, and deed number.
4. Confirm removal or continued presence.
5. If still present, request release letter or updated processing confirmation.
6. Retrieve a fresh extract close to closing if operationally supported.

## Workflow 8: Order and payment chain

### Goal

Use an adapter that requires an extract order and status polling.

### Steps

1. Create an extract order with block, parcel, subparcel, purpose, language, and payment reference.
2. Store the create response securely.
3. Extract `order_id` from the create response.
4. Pass the extracted `order_id` to the status endpoint.
5. Reconcile payment status before any retry.
6. Download or parse the final extract only after order status permits it.

### CLI pattern

```bash
CREATE_RESPONSE="$(land-registry-tabu --mock-file scripts/fixtures/sample_parcel_response.json --order-mock-file scripts/fixtures/sample_order_response.json create-order --block 30001 --parcel 12 --subparcel 4)"
ORDER_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["order_id"])' <<< "$CREATE_RESPONSE")"
land-registry-tabu --mock-file scripts/fixtures/sample_parcel_response.json --order-mock-file scripts/fixtures/sample_order_response.json order-status --order-id "$ORDER_ID"
```

## Workflow 9: Document pack for professional review

### Goal

Create a concise package for a lawyer, accountant, lender, or business owner.

### Include

- Raw extract.
- Normalized JSON.
- Summary of owners and shares.
- Encumbrance table.
- Warning flags.
- Questions for review.
- Retrieval timestamp.
- Source identifier and request ID.
- Copies of supporting documents: contract, municipal bill, company documents, probate order, bank letter, or planning documents.

## Review questions

Ask these questions in every serious transaction:

1. Is the property identifier exact?
2. Is the extract current?
3. Does the counterparty match the right holder?
4. Does the share match the transaction?
5. Are any mortgages, caveats, liens, attachments, leases, or easements registered?
6. Are non-Tabu registries involved?
7. Are planning, licensing, tax, or accounting checks needed separately?
8. Is professional legal review required before payment or signing?

## Quality gates

A workflow is complete only when:

- The normalized property identifier is stored.
- The raw response is retained.
- All owners and right holders are parsed.
- All encumbrances and warnings are listed.
- Unknowns are explicit.
- A fresh extract is recommended for high-value transactions.
