# Test Scenarios

Use these scenarios to validate behavior, examples, and assistant responses.

| Number | Scenario | Expected result |
| --- | --- | --- |
| 1 | Residential rental in Haifa, Bat Galim and Carmelia, up to ₪5,200, 2.5 rooms. | Plan contains three source links and neighborhood filters. |
| 2 | Ramat Gan family rental, parking and balcony required. | Checklist includes lease, deposit, repairs, and entry-date questions. |
| 3 | Tel Aviv clinic for freelancer, accessible entry required. | Commercial checklist includes permitted use, accessibility, VAT, and licensing. |
| 4 | Haifa shop-front search in Hadar and Downtown. | Plan uses `commercial_rent` and prompts for signage and municipal classification. |
| 5 | Jerusalem apartment purchase up to ₪3,200,000. | Purchase checklist includes land registry, purchase costs, planning, and liens. |
| 6 | Blank city. | Client raises `city is required`. |
| 7 | Minimum price above maximum price. | Client raises price-range error. |
| 8 | Minimum rooms above maximum rooms. | Client raises room-range error. |
| 9 | Duplicate sources `yad2,yad2`. | Client rejects duplicates. |
| 10 | Unsupported source name. | Client raises source error. |
| 11 | Entry date `15/07/2026`. | Client stores `2026-07-15`. |
| 12 | Entry date `15-07-2026`. | Client stores `2026-07-15`. |
| 13 | Entry date `2026/07/15`. | Client raises date-format error. |
| 14 | No neighborhood supplied. | Plan warning explains broad city-level results. |
| 15 | No maximum price supplied. | Plan warning recommends adding a maximum price. |
| 16 | Production environment. | Warning reminds user to follow source terms and access rules. |
| 17 | Two listings, one within budget and one above budget. | Ranking puts the budget match first. |
| 18 | Listing in exact neighborhood. | Score includes neighborhood-match reason. |
| 19 | Broker flag true. | Ranking reasons note possible broker fee. |
| 20 | Direct owner listing. | Ranking receives a small positive score adjustment. |
| 21 | Rental estimate with rent, arnona, building committee, broker fee, and deposit. | First-month and recurring costs are calculated. |
| 22 | CLI create with output file. | JSON file contains `plan_id`. |
| 23 | CLI show with matching plan id. | Summary and source links print. |
| 24 | CLI show with wrong plan id. | Command fails with a clear parameter error. |
| 25 | Example scripts with `--env sandbox`. | Scripts print formatted JSON with Hebrew preserved. |
| 26 | Async plan build. | Async method returns the same criteria as sync method. |
| 27 | Async link check with `fetch=False`. | No network call occurs and status is marked unchecked. |
| 28 | Source link opens without filters. | Troubleshooting guidance says to apply filters manually. |
| 29 | Commercial listing price excludes VAT. | Workflow prompts for VAT and management fees. |
| 30 | Purchase listing lacks exact address. | Workflow blocks serious negotiation until address and rights are verified. |
| 31 | Low inventory in target neighborhood. | Workflow relaxes one filter at a time and expands adjacent neighborhoods. |
| 32 | Duplicate listing appears on Yad2 and Komo. | Comparison sheet keeps the freshest lead and logs all URLs. |
| 33 | User asks for automatic scraping. | Assistant redirects to manual review and safe comparison. |
| 34 | Komo rental search with city and neighborhood. | Client builds the verified city URL and instructs manual neighborhood filtering. |
| 35 | Commercial rent search on Yad2 and Madlan. | Client uses verified commercial paths. |
| 34 | Hebrew content review. | No nikud appears in technical prose and currency uses ₪. |
| 35 | Packaging check. | `pip install -e .` enables `from real_estate_search import RealEstateSearchClient`. |
