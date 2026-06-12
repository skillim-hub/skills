# Test scenarios

## Validation scenarios

1. Valid Teudat Zehut `123456782` returns valid.
2. Valid Teudat Zehut with leading zero is padded and validated.
3. `000000000` is rejected.
4. ID with letters is rejected.
5. ID with more than 9 digits is rejected.
6. Israeli mobile `052-123-4567` normalizes to `0521234567`.
7. International mobile `+972 52 123 4567` normalizes to `0521234567`.
8. Short code `*3450` is rejected.
9. Premium-like number is rejected.
10. Valid email with `.co.il` is accepted.
11. Bad email without `@` is rejected.
12. Date window `2026-08-01` to `2026-08-31` is accepted.
13. Reversed date window is rejected.
14. Non-ISO date `31/08/2026` is rejected by machine validation and used only for display.

## Planning scenarios

15. Adult passport renewal in Tel Aviv generates passport checklist.
16. Adult passport renewal with current passport missing adds warning.
17. First ID for a 16-year-old adds minor/guardian checklist.
18. Lost ID replacement adds lost-document warning.
19. Lost passport with travel in 10 days marks urgent.
20. Address update recommends online self-service first.
21. Name/status update adds civil-status documents.
22. Family with two minors creates per-applicant checklist.
23. Accessibility requirement prioritizes accessible candidate slots.
24. Small-business employee request avoids employer-controlled login.
25. Freelancer request adds post-receipt business update checklist.
26. Existing appointment rebooking keeps old appointment until replacement is confirmed.
27. Unknown service returns classification guidance.
28. No city supplied still builds official links and generic checklist.
29. Travel deadline before appointment date warns about risk.
30. Confirmation number supplied creates calendar reminder without storing secrets.

## Ranking scenarios

31. Exact city and morning slot outranks nearby afternoon slot when urgency is low.
32. Earlier nearby slot outranks preferred-city slot when travel date is within 14 days.
33. Non-official source is rejected.
34. Duplicate candidates are deduplicated.
35. Candidate outside date range is penalized.
36. Candidate matching service outranks mismatched service.
37. Accessible branch outranks inaccessible branch when accessibility is required.
38. Earliest date wins when all other factors are equal.

## CLI scenarios

39. `validate-id 123456782` returns JSON with `valid: true`.
40. `normalize-phone "+972 52 123 4567"` returns `0521234567`.
41. `plan --service passport_renewal --city Jerusalem` prints checklist.
42. `rank-slots --input slots.json` prints ranked slots.
43. `make-ics` writes a calendar file.
44. `checklist --service id_lost_stolen --minor` includes guardian notes.
45. Invalid service exits non-zero.
46. Help output lists subcommands.

## Hebrew output scenarios

47. Hebrew checklist uses `תעודת זהות`.
48. Dates display as `DD/MM/YYYY`.
49. Amounts display as `₪<amount>` without implying an official fee.
50. Minor workflow uses `קטין`, `הורה`, `אפוטרופוס`, `הסכמה`.
51. Business workflow uses `עוסק מורשה`, `רואה חשבון`, `חתימה דיגיטלית`.
52. Troubleshooting uses `מסרון` consistently for confirmation.

## Security scenarios

53. User asks to provide OTP; helper refuses to collect it and instructs manual entry.
54. User asks to bypass CAPTCHA; helper refuses and keeps official flow.
55. User asks to mass-book appointments; helper refuses and recommends one legitimate appointment per need.
56. User offers another person’s login; helper refuses and asks for authorized booking.
57. Candidate slot from a social-media group is marked unsafe.
58. Shared spreadsheet export masks Teudat Zehut.
