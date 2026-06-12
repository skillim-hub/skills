from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal

from travel_booking_assistant import (
    Money,
    TravelBookingClient,
    TravelRequest,
    Traveler,
    TripType,
    duplicate_charge_triage,
    invoice_request_he,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    return parser.parse_args()


def client_for(env: str) -> TravelBookingClient:
    return TravelBookingClient(
        environment=env,
        default_fx_rates={
            "EUR": Decimal(os.getenv("TRAVEL_BOOKING_EUR_ILS", "3.3365")),
            "USD": Decimal(os.getenv("TRAVEL_BOOKING_USD_ILS", "2.8720")),
            "GBP": Decimal(os.getenv("TRAVEL_BOOKING_GBP_ILS", "3.8629")),
        },
        default_card_markup_percent=Decimal(os.getenv("TRAVEL_BOOKING_CARD_MARKUP", "2.8")),
    )


def context(env: str) -> dict[str, str]:
    return {
        "env": env,
        "api_base": os.getenv("TRAVEL_BOOKING_API_BASE", "sandbox.local"),
        "approval_owner": os.getenv("TRAVEL_APPROVAL_OWNER", "operations"),
    }


def main() -> None:
    args = parse_args()
    client = client_for(args.env)
    request = TravelRequest(
        trip_type=TripType.MIXED,
        origin=os.getenv("TRAVEL_ORIGIN", "Haifa"),
        destination=os.getenv("TRAVEL_DESTINATION", "Ben Gurion Airport and Berlin"),
        start_date=os.getenv("TRAVEL_START_DATE", "03/09/2026"),
        end_date=os.getenv("TRAVEL_END_DATE", "07/09/2026"),
        travelers=[Traveler("adult", 1)],
        passport_expiry=os.getenv("TRAVEL_PASSPORT_EXPIRY", "04/2027"),
        nationality=os.getenv("TRAVEL_NATIONALITY", "Israel"),
        environment=args.env,
    )
    created = client.create_request(request)
    request = TravelRequest(**{**request.as_dict(), "request_id": created["request_id"]})
    recommendation = client.quote_request(request)
    print(json.dumps({"context": context(args.env), "created": created, "recommendation": recommendation.as_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
