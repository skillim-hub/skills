# Troubleshooting

## No results returned after opening links

Likely causes:

- The neighborhood name differs between source sites.
- The price ceiling is below current supply.
- The room range is too narrow.
- The generated query parameter is not honored by the source site.

Fix:

1. Remove one filter at a time.
2. Search by city and one neighborhood name only.
3. Add nearby street names manually inside the source site.
4. Expand to one adjacent neighborhood.
5. Save the changed criteria and rerun the plan.

## Too many irrelevant results

Likely causes:

- City-level search without neighborhoods.
- Missing price ceiling.
- Broad property types.
- Commercial and residential listings mixed together.

Fix:

1. Add neighborhoods.
2. Add maximum price.
3. Add room minimum or property type.
4. Filter by newest first.
5. Remove duplicate listings before calling advertisers.

## Source site ignores filters

Generated links are helpers, not guaranteed private API calls. A commercial site may change query names or ignore parameters. Komo city pages are generated with verified visible path patterns; neighborhood filtering remains a manual check unless a verified neighborhood id is available.

Fix:

1. Open the link manually.
2. Apply the missing filter in the site interface.
3. Save the corrected URL if the browser reflects it.
4. Update tests when a source adapter changes.

## Listing data conflicts across sources

Example conflicts:

- One source says 3 rooms, another says 3.5.
- Photos match but price differs.
- Broker status differs.
- Neighborhood label differs from map location.

Fix:

1. Treat the listing as unverified.
2. Ask for exact address and written details.
3. Prefer official documents for rights, planning, taxes, and municipal classification.
4. Keep every conflicting URL in the comparison sheet.

## Broker fee surprise

Fix:

1. Ask whether the advertiser is a licensed broker, owner, or tenant.
2. Request written confirmation of any fee before a visit.
3. For brokerage, confirm a written brokerage agreement before any fee claim.
4. Include broker fee in first-month cash calculations.

## Commercial use is uncertain

Fix:

1. Ask for the permitted use and current municipal classification.
2. Contact the municipality or a qualified professional before signing.
3. Check business licensing, accessibility, signage, fire-safety, storage, and customer access.
4. Treat vague assurances as insufficient.

## Price excludes VAT or fees

Commercial listings often state rent before VAT or exclude management fees.

Fix:

1. Ask whether the price includes VAT.
2. Ask for management fee, arnona, utilities, parking, storage, and maintenance charges.
3. Compare total monthly cost, not only rent.

## Hebrew date rejected by CLI

Accepted formats:

- `2026-07-15`
- `15/07/2026`
- `15-07-2026`

Fix the date and rerun the command.

## CLI command not found

Fix:

```bash
pip install -e .
real-estate-search --help
```

When using a virtual environment, activate it before running the command.

## Imports fail in scripts

Fix:

```bash
pip install -e .
python scripts/examples/search_family_rental.py --env sandbox
```

Do not add local path hacks to examples. Install the package in editable mode.

## Pytest cannot find async support

Fix:

```bash
pip install -r requirements-dev.txt
pytest
```

The development requirements include `pytest-asyncio`.

## User wants automatic scraping

Safe response:

- Explain that generated links support manual review.
- Offer a comparison template and a checklist.
- Do not bypass source controls, rate limits, logins, or terms.

## User asks for legal or tax certainty

Safe response:

- Provide a checklist and official-source pointers.
- Avoid giving current tax rates unless checked from an official source. As of the 04/06/2026 verification pass, official sources still support using 18% as the standard VAT assumption from 01/01/2025, but recheck before quoting it in a live transaction.
- Recommend qualified professional review for purchase, lease, business licensing, and tax questions.
