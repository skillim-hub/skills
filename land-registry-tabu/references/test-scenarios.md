# Test Scenarios

Use these scenarios to validate client behavior, CLI output, workflow completeness, and report quality.

## Core lookup scenarios

1. Exact apartment lookup: block 30001, parcel 12, subparcel 4 returns one owner and no warnings.
2. Shared ownership: two owners each hold `1/2`; report lists both and validates total share context.
3. Company owner: right holder is a company; report flags signatory authority check.
4. Parcel without subparcel: block and parcel only; report warns that units may require additional verification.
5. Nonexistent parcel: service returns no rights and a not-found warning.
6. Ambiguous address: address lookup returns multiple candidate parcels; no definitive ownership statement.
7. Address candidate confirmed: address lookup maps to one candidate and then parcel lookup succeeds.
8. Apartment number mismatch: address apartment number differs from subparcel; report flags mismatch.

## Encumbrance scenarios

9. Mortgage exists: report lists bank beneficiary, amount in `₪`, date, and release or consent action.
10. Mortgage released in newer extract: compare old and new responses and mark removed.
11. Caveat exists: report identifies beneficiary and asks for legal basis.
12. Attachment exists: report marks high-risk and requires legal review.
13. Easement exists: report flags access and use implications.
14. Long lease exists: report flags lease term and transfer review.
15. Multiple encumbrances: report groups mortgage, caveat, and attachment without overwriting one another.
16. Encumbrance has no amount: report keeps beneficiary and type, then marks amount unknown.

## Data quality scenarios

17. Hebrew-key payload: parser extracts property, owners, shares, and warnings from Hebrew keys.
18. English-key payload: parser extracts the same normalized structure from English keys.
19. Missing owner ID: report does not fail; ID is marked unavailable.
20. Invalid Israeli ID: validation returns false and does not crash.
21. Foreign or company ID: ID validation is skipped unless explicitly requested for personal ID.
22. Share as percent: `50%` normalizes to `1/2`.
23. Share as decimal: `0.25` normalizes to `1/4`.
24. Unknown share: parser preserves raw value and flags review need.

## Operational scenarios

25. 401 unauthorized: client raises a structured API error.
26. 402 payment required: client raises a structured API error and does not retry automatically.
27. 429 rate-limited: caller can retry with backoff.
28. Timeout on read-only lookup: caller can retry idempotent operation.
29. Paid order conflict: client exposes conflict status for reconciliation.
30. CLI mock mode: local JSON fixture returns normalized JSON without network access.
31. CLI table mode: output redacts IDs.
32. Async parcel lookup: async wrapper returns the same normalized extract as sync lookup.
33. Raw payload retention: `raw` exists in normalized extract for audit.
34. Privacy check: report uses masked IDs only.
35. Old extract date: workflow flags freshness issue.
36. Registry type mismatch: record suggests Israel Land Authority or housing company path; report stops short of ownership conclusion.
37. Create-order chain: create response returns `order_id`; status request uses the extracted value.
38. Installable import: `from land_registry_tabu import LandRegistryTabuClient` works after `pip install -e .`.
39. Example scripts: each example accepts `--env sandbox|production`.
40. Syntax check: `python -m compileall scripts/ -q` succeeds.

## Acceptance criteria

A scenario passes only when:

- The response is deterministic.
- Personal IDs are masked in summaries.
- Unknowns are explicit.
- Encumbrances are not dropped.
- Errors are structured.
- Paid operations are not blindly retried.
- Legal conclusions are avoided.
