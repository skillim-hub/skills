# Test Scenarios

Use these scenarios for manual QA, regression testing, and acceptance review.

| # | Scenario | Steps | Expected result |
|---:|---|---|---|
| 1 | Tax form discovery by number | Discover `tax-authority-public-forms` with query `1301`. | Relevant public results only. |
| 2 | Tax form discovery by Hebrew term | Discover with query `דוח שנתי`. | Hebrew query matches titles or URLs. |
| 3 | National Insurance benefit form | Discover `bituach-leumi-forms` with query `דמי לידה`. | Public forms are returned or no-match is explicit. |
| 4 | General gov.il query | Discover `gov-il-services` with query `שינוי כתובת` and limit 10. | Broad source is constrained. |
| 5 | Corporations source | Discover `corporations-authority` with query `עמותה`. | Public registry forms are discovered when links are direct. |
| 6 | No query broad guard | Run discovery with small max-results. | Command completes and does not download unless requested. |
| 7 | Unknown source | Run discover with missing source. | Source error is raised. |
| 8 | Direct file source | Registry points directly to a public PDF. | Record is created for the file. |
| 9 | HTML with duplicate links | Fixture contains same PDF twice. | Duplicate URL appears once. |
| 10 | Hebrew title file name | Download title with Hebrew and unsafe characters. | Output file preserves Hebrew and removes unsafe characters. |
| 11 | Checksum added | Track a newly downloaded file. | Status is `added`. |
| 12 | Checksum unchanged | Track same file twice. | Status is `unchanged` on second run. |
| 13 | Checksum updated | Change fixture bytes and track again. | Status is `updated`. |
| 14 | CSV export | Export manifest after a download. | CSV opens with Hebrew text. |
| 15 | Saved request chain | Create request, extract id, run request. | Same id appears in run response. |
| 16 | Bad request id | Run request with malformed id. | Request-not-found error is raised. |
| 17 | Async discover | Call `async_discover` on fixture. | Results match sync discover. |
| 18 | Async refresh | Call `async_refresh_source` on fixture. | Downloaded file is tracked. |
| 19 | Phone mobile | Validate `052-1234567`. | Local and international formats returned. |
| 20 | Phone international | Validate `+972521234567`. | Valid mobile result returned. |
| 21 | Landline | Validate `03-1234567`. | Valid landline result returned. |
| 22 | Bad phone | Validate `071-1234567`. | Invalid result returned. |
| 23 | Identity number | Validate `123456782`. | Valid structural result returned. |
| 24 | Postal code | Validate `6100001`. | Valid seven-digit result returned. |
| 25 | Invalid environment | Create client with unsupported environment. | ValueError is raised. |
| 26 | Compile scripts | Run `python -m compileall scripts/ -q`. | No syntax errors. |

| 21 | Web-validated gov.il services URL | Inspect default registry. | `gov-il-services` uses `https://www.gov.il/he/services`. |
| 22 | Web-validated corporations URL | Inspect default registry. | `corporations-authority` uses `israeli_corporations_authority`. |
| 23 | National Insurance certificates source | List sources. | `bituach-leumi-certificates` is present. |
| 24 | Bituach Leumi inactive search fallback | Use certificates or forms category query. | Workflow does not depend on inactive search page. |
