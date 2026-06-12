# Test Scenarios

1. Hebrew CSV with `מספר קופה`, `שם קופה`, `תאריך דיווח`: fields normalize.
2. English CSV with `fund_id`, `fund_name`, `report_date`: fields normalize.
3. UTF-8-SIG Hebrew file: header parses.
4. Windows-1255 file: documented retry path works after conversion or encoding override.
5. Decimal comma `1,23`: value becomes `1.23`.
6. Thousands separator `1,234.56`: value becomes `1234.56`.
7. Currency `₪2,000`: value becomes `2000`.
8. Percent `0.20%`: value becomes `0.2`.
9. Month-only `12/2025`: date becomes `2025-12-01`.
10. ISO date `2025-12-31`: date parses.
11. DD-MM-YYYY `31/12/2025`: date parses.
12. Missing fund ID: critical validation issue.
13. Missing fee fields: load succeeds; fee analysis caveats are required.
14. Negative monthly return `-2.4`: accepted if plausible.
15. Return `150`: implausible-return warning.
16. Asset fee `25`: implausible-fee warning.
17. Two funds with different report dates: direct ranking warns or aligns periods.
18. Exact duplicate row: duplicate warning.
19. Same fund in November and December: latest ranking uses December.
20. Ranking by 36M return: sorted descending.
21. Ranking by asset fee ascending: lowest fee first.
22. Compare IDs `12345`, `67890`: only selected funds appear.
23. Fee impact with zero fees: net equals gross.
24. Fee impact with fees: net is lower than gross.
25. Composite score with missing 60M return: score uses available fields and caveat.
26. Non-official marketing source: rejected as primary source.
27. User asks "which fund should I choose?": advice declined; neutral comparison offered.
28. Employer aggregate overview: aggregate only, no employee-level data.
29. CKAN `success: false`: clear data-source error.
30. CKAN pagination: fetch continues until total is reached.

Acceptance criteria:
- Source and period appear in reports.
- No recommendation is made.
- Percentage points are handled consistently.
- Incomparability is flagged.
- Hebrew reports use professional terminology and `₪` formatting.
