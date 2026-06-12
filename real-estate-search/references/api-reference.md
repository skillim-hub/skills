# Reference: Sources, Schemas, Regulations, and Error Handling

## Scope

This skill is a non-API listing workflow. It builds structured search plans and source links for Yad2, Madlan, and Komo, then guides manual verification. It does not claim a private or official listing API for those commercial sites. Verified path support is recorded in `references/verification-log.md`; query parameters are conservative helper hints unless explicitly listed as verified.

## Source adapters

### Common request schema

```json
{
  "city": "חיפה",
  "deal_type": "rent",
  "neighborhoods": ["בת גלים", "כרמליה"],
  "max_price": 5200,
  "min_rooms": 2.5,
  "property_types": ["דירה"],
  "parking": true,
  "balcony": true,
  "entry_date": "15/07/2026",
  "sources": ["yad2", "madlan", "komo"]
}
```

### Common response schema

```json
{
  "plan_id": "res-3c329ddf9a61",
  "environment": "sandbox",
  "created_at": "2026-06-04T00:00:00Z",
  "criteria": {
    "city": "חיפה",
    "deal_type": "rent",
    "neighborhoods": ["בת גלים", "כרמליה"],
    "max_price": 5200,
    "min_rooms": 2.5
  },
  "links": [
    {
      "source": "yad2",
      "url": "https://www.yad2.co.il/realestate/rent?...",
      "label": "yad2 search for חיפה",
      "manual_steps": ["Open the link and confirm filters manually."]
    }
  ],
  "review_checklist": ["Confirm the exact street and building entrance before scheduling a visit."],
  "warnings": ["No neighborhood filter supplied; results may include broad city-level matches."]
}
```

### Yad2 adapter

| Field | Behavior |
| --- | --- |
| Base URL | `https://www.yad2.co.il/realestate` |
| Rent path | `/rent` |
| Sale path | `/forsale` |
| Commercial path | `/commercial` |
| Search mode | Generated link for manual browser review. |
| Verified visible controls | Transaction type, location hierarchy including neighborhood, and commercial category are visible in public pages. |
| Required manual checks | Availability, exact address, advertiser role, broker fee, source freshness. |

Example generated link pattern:

```text
https://www.yad2.co.il/realestate/rent?city=חיפה&neighborhood=בת+גלים&max_price=5200&min_rooms=2.5
```

### Madlan adapter

| Field | Behavior |
| --- | --- |
| Base URL | `https://www.madlan.co.il` |
| Rent path | `/for-rent` |
| Sale path | `/for-sale` |
| Commercial rent path | `/commercial/for-rent/{location}` |
| Commercial sale path | `/commercial/for-sale/{location}` |
| Search mode | Generated link for manual browser review. |
| Required manual checks | Map position, neighborhood context, comparable prices, planning signals. |

Example generated link pattern:

```text
https://www.madlan.co.il/for-rent?city=חיפה&neighborhood=בת+גלים&max_price=5200
```

### Komo adapter

| Field | Behavior |
| --- | --- |
| Base URL | `https://www.komo.co.il` |
| Rent city path | `/code/nadlan/apartments-for-rent.asp?cityName={city}&nehes=1` |
| Sale city path | `/code/nadlan/apartments-for-sale.asp?cityName={city}&nehes=1` |
| Commercial rent helper path | `/code/nadlan/apartments-for-rent.asp?cityName={city}&nehes=28` for shops or commercial space. |
| Verified room parameters | `fromRooms`, `toRooms` appear in public indexed result URLs. |
| Search mode | Generated link for manual browser review. |
| Neighborhood handling | Public pages show neighborhood labels in listings; do not assume a neighborhood-name query parameter. Apply neighborhood filtering manually unless a verified `neighborhoodNum` is known. |
| Required manual checks | Freshness, duplicate listings, exact property details. |

Example generated link pattern:

```text
https://www.komo.co.il/code/nadlan/apartments-for-rent.asp?cityName=חיפה&nehes=1&fromRooms=3
```

## Public Israeli references to verify outside listing sites

Use current official pages before making a financial or legal decision. Names and links are provided as a reference index, not as live legal advice.

| Topic | Official source to check | Use in workflow |
| --- | --- | --- |
| Land registry and rights | Ministry of Justice land registration services, `https://www.gov.il/he/departments/land_registration` | Verify ownership, liens, rights, and current extract before purchase. |
| Real-estate taxation | Israel Tax Authority, `https://www.gov.il/he/departments/israel_tax_authority` | Check purchase tax, capital gains tax context, and current rates. |
| Planning information | Planning Administration and local planning portals, including national planning systems | Check plans, permits, betterment levy exposure, and zoning constraints. |
| Municipal arnona | Relevant municipality website and arnona department | Confirm residential or business classification and monthly charge. |
| Business licensing | Relevant municipality business licensing department and Business Licensing Law guidance | Confirm that the intended business activity can operate at the address. |
| Accessibility | Commission for Equal Rights of Persons with Disabilities and applicable accessibility regulations | Check accessibility duties for public-facing businesses. |
| Consumer protection | Consumer Protection and Fair Trade Authority | Check advertising, brokerage, and consumer-facing conduct. |
| Privacy | Privacy Protection Authority and Privacy Protection Law requirements | Limit storage of advertiser and user personal data. |
| Brokerage | Real Estate Brokers Law and Ministry of Justice broker registry | Confirm licensed broker status and written fee agreement. |
| Residential lease | Rental and Lending Law and lease-specific consumer guidance | Review deposits, repairs, renewal, exit terms, and guarantees. |
| Public datasets | Israel Government Data Portal, `https://data.gov.il`, and CKAN documentation at `https://data.gov.il/docs` | Look up locality identifiers or public datasets when needed. |

## Error table

| Error | Likely cause | Recovery |
| --- | --- | --- |
| `city is required` | Blank city field. | Ask for a city or local council name. |
| `deal_type must be rent, sale, commercial_rent, or commercial_sale` | Unsupported transaction type. | Map the user request to one supported value. |
| `min_price must not exceed max_price` | Reversed price range. | Swap values or ask for a corrected budget. |
| `min_rooms must not exceed max_rooms` | Reversed room range. | Swap values or remove one bound. |
| `source must be yad2, madlan, or komo` | Unsupported source name. | Use the three supported sources only. |
| `sources must not contain duplicates` | Repeated source in input. | Deduplicate the source list. |
| `entry_date must use YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY` | Date format not supported. | Use `15/07/2026` for Israeli display or `2026-07-15` for storage. |
| Source page opens without filters | Site changed query handling. | Apply filters manually and update adapter tests. |
| Too many duplicates | Same property listed by owner and broker. | Keep the most current listing, log all URLs, and confirm the advertiser role. |
| Commercial suitability unclear | Listing lacks zoning or use details. | Contact municipality or relevant professional before negotiation. |

## Request and response examples

### Build plan in Python

```python
from real_estate_search import RealEstateSearchClient

client = RealEstateSearchClient("sandbox")
plan = client.build_search_plan({
    "city": "גבעתיים",
    "deal_type": "rent",
    "neighborhoods": "בורוכוב,שינקין",
    "max_price": 7800,
    "min_rooms": 3,
})
print(plan.to_json())
```

### Rank manually collected listings

```python
from real_estate_search import RealEstateSearchClient

client = RealEstateSearchClient("sandbox")
ranked = client.rank_listings(
    [
        {"title": "דירה א", "city": "חיפה", "neighborhood": "בת גלים", "price": 4900, "rooms": 3},
        {"title": "דירה ב", "city": "חיפה", "neighborhood": "הדר", "price": 5400, "rooms": 3}
    ],
    {"city": "חיפה", "neighborhoods": "בת גלים", "max_price": 5200, "min_rooms": 2.5}
)
```

### Estimate rental cash needed

```python
from real_estate_search import RealEstateSearchClient

client = RealEstateSearchClient("sandbox")
estimate = client.estimate_monthly_cash_needed(
    {"title": "דירה", "city": "חיפה", "price": 5000},
    monthly_arnona=400,
    monthly_vaad_bayit=250,
    broker_fee_months=1,
    deposit_months=2,
)
print(estimate.to_dict())
```

## Data handling rules

- Store only the minimum personal data required to progress a property lead.
- Prefer links, listing ids, and business contact details over free-form personal notes.
- Do not publish advertiser phone numbers or private messages outside the transaction workflow.
- Delete stale leads when no longer needed.
- Keep user budget, family status, health, disability, and business information confidential.
