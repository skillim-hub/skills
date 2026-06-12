# Travel-Booking Assistant

A neutral, branding-free skill package for booking and supporting Israeli domestic and international travel. It is designed for Israeli small businesses, freelancers, and consumers who need structured booking decisions, ₪ cost summaries, exchange-rate handling, invoice prompts, and supplier troubleshooting.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with request chaining

Create a request, extract its ID, and use that ID in the next step:

```bash
CREATE_RESPONSE=$(travel-booking-assistant create-request \
  --trip-type domestic \
  --origin "Tel Aviv" \
  --destination "Eilat" \
  --start-date 12/06/2026 \
  --end-date 14/06/2026 \
  --adults 1 \
  --business \
  --needs-vat-invoice \
  --env sandbox)

REQUEST_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["request_id"])' <<< "$CREATE_RESPONSE")

travel-booking-assistant quote \
  --request-id "$REQUEST_ID" \
  --trip-type domestic \
  --origin "Tel Aviv" \
  --destination "Eilat" \
  --start-date 12/06/2026 \
  --end-date 14/06/2026 \
  --adults 1 \
  --business \
  --needs-vat-invoice \
  --env sandbox
```

The same commands can be run through the script wrapper:

```bash
python scripts/travel-booking-assistant-cli.py create-request --trip-type domestic --origin "Tel Aviv" --destination "Eilat" --start-date 12/06/2026 --end-date 14/06/2026 --adults 1 --env sandbox
```

## Import quick start

```python
from travel_booking_assistant import TravelBookingClient, TravelRequest, Traveler, TripType

request = TravelRequest(
    trip_type=TripType.DOMESTIC,
    origin="Tel Aviv",
    destination="Eilat",
    start_date="12/06/2026",
    end_date="14/06/2026",
    travelers=[Traveler("adult", 1)],
    business=True,
    needs_vat_invoice=True,
)

client = TravelBookingClient(environment="sandbox")
created = client.create_request(request)
request_with_id = TravelRequest(**{**request.as_dict(), "request_id": created["request_id"]})
recommendation = client.quote_request(request_with_id)
print(client.to_json(recommendation))
```

## Tests

```bash
pytest -q
python -m compileall scripts/ -q
```

## Examples

Every example reads environment variables, accepts `--env sandbox|production`, and prints JSON with `ensure_ascii=False` and `indent=2`.

```bash
python scripts/examples/eilat_business_trip.py --env sandbox
python scripts/examples/berlin_business_trip.py --env sandbox
python scripts/examples/rail_to_airport.py --env sandbox
python scripts/examples/missing_invoice_request.py --env sandbox
python scripts/examples/duplicate_charge_triage.py --env sandbox
python scripts/examples/hebrew_eilat_quote.py --env sandbox
```

Supported environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `TRAVEL_BOOKING_API_BASE` | External integration base URL placeholder | `sandbox.local` |
| `TRAVEL_BOOKING_EUR_ILS` | EUR to ₪ rate for deterministic examples | `3.3365` |
| `TRAVEL_BOOKING_USD_ILS` | USD to ₪ rate for deterministic examples | `2.8720` |
| `TRAVEL_BOOKING_GBP_ILS` | GBP to ₪ rate for deterministic examples | `3.8629` |
| `TRAVEL_BOOKING_CARD_MARKUP` | Card markup percent | `2.8` |
| `TRAVEL_APPROVAL_OWNER` | Approval owner label for examples | `operations` |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide with examples, decision trees, edge cases, anti-patterns, and production checklist. |
| `SKILL_HE.md` | Hebrew operating guide localized for Israeli terminology, ₪, and DD/MM/YYYY. |
| `references/api-reference.md` | Israeli API/regulation source reference, request/response examples, and error tables. |
| `references/workflow-guide.md` | End-to-end workflows for domestic, rail, international, cancellation, invoice, and payment cases. |
| `references/troubleshooting.md` | Operational troubleshooting guide and escalation templates. |
| `references/test-scenarios.md` | 30 concrete QA scenarios. |
| `references/migration-checklist.md` | Migration checklist from older skills or manual workflows. |
| `references/branding-audit.md` | Verification report for neutral packaging and visual-reference removal. |
| `references/hebrew-qa-log.md` | Hebrew localization and terminology QA log. |
| `travel_booking_assistant/` | Installable Python package. |
| `scripts/travel-booking-assistant-cli.py` | CLI wrapper. |
| `scripts/test_travel_booking_assistant_client.py` | Pytest suite with more than 20 tests. |
| `scripts/examples/` | Runnable scenario examples. |

## CLI examples

Domestic Eilat quote:

```bash
travel-booking-assistant quote \
  --trip-type domestic \
  --origin "Tel Aviv" \
  --destination "Eilat" \
  --start-date 12/06/2026 \
  --end-date 14/06/2026 \
  --adults 1 \
  --business \
  --needs-vat-invoice \
  --env sandbox
```

International quote with FX:

```bash
travel-booking-assistant quote \
  --trip-type international \
  --origin "Tel Aviv" \
  --destination "Berlin" \
  --start-date 03/09/2026 \
  --end-date 07/09/2026 \
  --adults 1 \
  --business \
  --supplier-currency EUR \
  --supplier-amount 912.50 \
  --fx-rate 3.3365 \
  --card-markup 2.8 \
  --env sandbox
```

## Design principles

- Keep every recommendation quote-only until a confirmed booking reference exists.
- Keep original currency and ₪ estimate together.
- Add source and timestamp for every foreign-exchange rate.
- Require human approval before payment or cancellation.
- Keep sensitive documents and card data out of free-text logs.
- Use Hebrew accounting terminology correctly.
- Avoid promotional framing and visual marks.

## Safety and compliance

This package provides operational support. It does not replace qualified legal, tax, immigration, insurance, accessibility, or accounting advice. Verify material decisions with the relevant supplier, regulator, or professional adviser.
