# API and Regulatory Reference

This reference lists practical Israeli and travel-sector sources to consult when implementing the Travel-Booking Assistant. Treat all examples as integration patterns unless live credentials and current terms are confirmed.


## Web-validated official values as of 04/06/2026

Use these values only as a documented validation baseline. Recheck before production use.

| Area | Verified value | Source handling |
|---|---|---|
| Standard Israeli VAT rate | 18%, effective from 01/01/2025 and still current in 2026 sources checked | Use in invoice prompts; do not decide deductibility. |
| Israel Invoices threshold | Above ₪10,000 before VAT from 01/01/2026; above ₪5,000 before VAT from 01/06/2026 | For input VAT deduction workflows, verify allocation number needs. |
| Bank of Israel sample rates | USD/ILS 2.8720, EUR/ILS 3.3365, GBP/ILS 3.8629, up-to-date as of 03/06 on the Bank of Israel page | Examples use these as deterministic defaults; live production must fetch current rates. |
| Bank of Israel data host | `edge.boi.gov.il` and series browser/API services | Prefer official data access and store timestamp. |
| Public transport static data | GTFS | Treat as static planned schedules; verify disruptions separately. |
| Public transport real-time data | SIRI interfaces | Treat as real-time operational data, subject to access and licensing. |
| Travel supplier webhooks | Not applicable in this package | Do not invent event names. Add only when a real supplier API is connected. |

### Israel Invoices 2026 operational note

For Israeli business travel expenses, when an Israeli supplier issues a tax invoice above the applicable threshold, record whether an allocation number is required and present. As of the validation date, the threshold moved to ₪5,000 before VAT from 01/06/2026. This affects bookkeeping review; it does not make the assistant a tax adviser.

### Bank of Israel production endpoint note

The Bank of Israel documentation points to the series database at `edge.boi.gov.il`. Use official series/API documentation rather than placeholder hosts. Store rate, publication date, retrieval timestamp, and whether a rate came from an official representative-rate source or a card/supplier estimate.


## Source hierarchy

1. Official government or regulator source.
2. Supplier API or documented partner API.
3. Licensed data feed.
4. Manual supplier confirmation.
5. Public website only when terms allow operational use.

Do not bypass authentication, rate limits, CAPTCHA, robots restrictions, or commercial licensing.

## Israeli sources

| Area | Source class | Use | Notes |
|---|---|---|---|
| Exchange rates | Bank of Israel public exchange-rate data | Convert foreign travel costs to ₪ | Indicative rates, not card settlement. |
| Public transport | Ministry of Transport public transit data / GTFS where available | Routes, stops, schedules | Check license and freshness. |
| Rail | Israel Rail schedule and service channels | Domestic rail itinerary checks | Use official or licensed data only. |
| Airports | Airport operator notices and Civil Aviation Authority information | Airport constraints, safety, delays | Do not infer flight status from general notices. |
| Passports and borders | Population and Immigration Authority | Passport and border prompts | Do not provide final immigration advice. |
| Tax and invoices | Israel Tax Authority | VAT invoice terminology and recordkeeping prompts | Direct tax advice requires a professional. |
| Consumer protection | Consumer Protection and Fair Trade Authority / applicable consumer law resources | Cancellation and disclosure prompts | Rules vary by supplier, channel, and transaction. |
| Accessibility | Equal Rights for Persons with Disabilities resources and supplier accessibility pages | Accessibility prompts | Confirm directly with supplier. |

## Bank of Israel exchange rates

Use for indicative conversion into ₪ when supplier amounts are in foreign currency.

### Operational rule

- Store original currency and amount.
- Store rate, source, and timestamp.
- Use card settlement data when available.
- Add card markup estimate separately.

### Example request pattern

```http
GET /currency/rates?currency=EUR&date=04/06/2026 HTTP/1.1
Host: edge.boi.gov.il
Accept: application/json
```

### Example response pattern

```json
{
  "source": "Bank of Israel",
  "currency": "EUR",
  "base_currency": "ILS",
  "date": "04/06/2026",
  "rate": 3.3365,
  "indicative": true
}
```

### Error table

| Status | Meaning | Handling |
|---:|---|---|
| 400 | Unsupported currency or date | Ask for a valid ISO currency/date; keep quote pending. |
| 404 | No rate for date | Try previous business day; flag the substitution. |
| 429 | Rate limit | Retry with backoff and cached recent rate if policy allows. |
| 500 | Source unavailable | Use approved fallback source and mark estimate. |

## Ministry of Transport / GTFS-style public transport data

Use for schedule planning, station/stop matching, and last-mile warnings.

### Example station lookup

```http
GET /stops?query=Tel%20Aviv%20Savidor HTTP/1.1
Host: example-transport-source
Accept: application/json
```

### Example response

```json
{
  "stops": [
    {
      "stop_id": "rail_tlv_savidor",
      "name_he": "תל אביב סבידור מרכז",
      "name_en": "Tel Aviv Savidor Center",
      "mode": "rail",
      "city": "Tel Aviv-Yafo"
    }
  ],
  "license": "check-current-feed-license",
  "generated_at": "04/06/2026T03:00:00+03:00"
}
```

### Example trip plan

```http
GET /journeys?from=rail_tlv_savidor&to=rail_bgu_airport&date=12/06/2026&arrive_by=08:30 HTTP/1.1
Host: example-transport-source
Accept: application/json
```

### Error table

| Status | Meaning | Handling |
|---:|---|---|
| 400 | Invalid stop or date | Ask for city/station clarification. |
| 404 | No journey found | Suggest taxi, bus, different station, or time change. |
| 409 | Service disruption | Present disruption and alternatives. |
| 429 | Rate limit | Retry with backoff; avoid repeated searches. |
| 503 | Feed unavailable | Mark schedule unverified and request manual check. |

## Airline availability and booking APIs

Use airline or accredited distribution APIs only under valid credentials and commercial terms.

### Search request

```http
POST /air/search HTTP/1.1
Host: example-air-provider
Content-Type: application/json
Idempotency-Key: tb-search-20260604-001

{
  "origin": "TLV",
  "destination": "BER",
  "departure_date": "03/09/2026",
  "return_date": "07/09/2026",
  "passengers": [{"type": "ADT", "count": 1}],
  "currency": "ILS",
  "include_baggage": true
}
```

### Search response

```json
{
  "offers": [
    {
      "offer_id": "ofr_123",
      "valid_until": "04/06/2026T14:15:00Z",
      "total": {"amount": 392.50, "currency": "EUR"},
      "baggage": {"carry_on": true, "checked_bag": false},
      "changeable": false,
      "refundable": false,
      "segments": [
        {"from": "TLV", "to": "BER", "departure": "03/09/2026T08:20:00+03:00"}
      ]
    }
  ]
}
```

### Booking request

```http
POST /air/book HTTP/1.1
Host: example-air-provider
Content-Type: application/json
Idempotency-Key: tb-book-20260604-001

{
  "offer_id": "ofr_123",
  "travelers": [
    {"given_name": "Dana", "family_name": "Levi", "date_of_birth": "1987-05-11"}
  ],
  "payment_mode": "manual_approval"
}
```

### Booking response

```json
{
  "status": "confirmed",
  "booking_reference": "ABC123",
  "ticketing_deadline": "04/06/2026T15:00:00Z",
  "documents": ["itinerary_receipt"]
}
```

### Airline error table

| Code | Meaning | Handling |
|---|---|---|
| OFFER_EXPIRED | Fare expired before booking | Re-price and ask for approval. |
| NAME_INVALID | Passenger name does not match format | Correct before payment. |
| BAGGAGE_UNAVAILABLE | Requested baggage cannot be added | Offer another fare or separate purchase. |
| PAYMENT_AUTH_REQUIRED | 3DS/manual approval needed | Pause and request secure payment flow. |
| TICKET_PENDING | Booking exists but ticket not issued | Do not mark final; monitor deadline. |
| SCHEDULE_CHANGED | Supplier changed schedule | Present options and fare rules. |

## Hotel APIs and supplier confirmations

### Search request

```http
POST /hotel/search HTTP/1.1
Host: example-hotel-provider
Content-Type: application/json

{
  "destination": "Eilat",
  "check_in": "12/06/2026",
  "check_out": "2026-06-14",
  "occupancy": [{"adults": 2, "children": 0}],
  "currency": "ILS",
  "invoice_required": true
}
```

### Search response

```json
{
  "properties": [
    {
      "property_id": "eilat_001",
      "name": "Example North Beach Hotel",
      "rate_id": "rate_789",
      "total": {"amount": 1820.00, "currency": "ILS"},
      "vat_invoice_available": true,
      "cancellation": {
        "free_until": "2026-06-09T18:00:00+03:00",
        "penalty": {"amount": 910.00, "currency": "ILS"}
      },
      "local_fees": []
    }
  ]
}
```

### Hotel error table

| Code | Meaning | Handling |
|---|---|---|
| RATE_CHANGED | Hotel price changed | Recalculate and request approval. |
| ROOM_UNAVAILABLE | Room sold out | Offer alternatives. |
| INVOICE_UNSUPPORTED | Requested invoice type unavailable | Warn and offer supplier change. |
| LOCAL_TAX_UNKNOWN | Local tax not returned | Mark local payment risk. |
| CARD_DEPOSIT_REQUIRED | Deposit required at property | Add to traveler checklist. |

## Consumer cancellation prompts

Before a consumer booking, record supplier identity, booking channel, cancellation deadline, cancellation fee, product type, applicable channel, and confirmation delivery method. Do not give final legal conclusions. Present operational facts and suggest professional or regulator review for disputed cancellation rights.

## Israeli tax and VAT prompts

For business bookings, ask:

1. Is the supplier Israeli or foreign?
2. Is the document a חשבונית מס, קבלה, חשבונית מס/קבלה, foreign invoice, or pro-forma?
3. Is Israeli VAT shown separately?
4. Is the expense business-related and approved internally?
5. Is the foreign-currency conversion evidence stored?
6. Is the original document retained?

| Supplier document | Hebrew term | Operational handling |
|---|---|---|
| Tax invoice | חשבונית מס | Store for VAT/accounting review. |
| Receipt | קבלה | Store as proof of payment. |
| Tax invoice/receipt | חשבונית מס/קבלה | Store as combined document. |
| Pro-forma invoice | חשבון עסקה / פרופורמה | Not proof of payment by itself. |
| Foreign invoice | חשבונית ספק זר | Store with FX evidence; VAT treatment may differ. |

## Security requirements

- Use TLS for all supplier calls.
- Store API keys in environment variables or a secret manager.
- Redact passport number, Israeli ID number, phone number, card number, and email in logs where practical.
- Use least-privilege API credentials.
- Use idempotency keys for booking and payment operations.
- Keep booking audit logs separate from public chat transcripts.
- Delete sensitive passenger data according to retention policy.

## Live integration checklist

- Verify current API terms and allowed use.
- Verify rate limits.
- Verify production and sandbox endpoints.
- Implement retries only for safe operations.
- Never retry payment blindly.
- Reprice expired offers.
- Keep timestamps in ISO 8601 internally and DD/MM/YYYY in Israeli-facing text.
- Test Hebrew names, English passport names, apostrophes, hyphens, and multiple surnames.
- Test ₪, USD, EUR, GBP, and mixed-currency lines.
