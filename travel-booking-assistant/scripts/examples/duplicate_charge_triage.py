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
    result = duplicate_charge_triage(
        [
            Money(os.getenv("TRAVEL_CHARGE_A", "420"), os.getenv("TRAVEL_CURRENCY_A", "EUR")),
            Money(os.getenv("TRAVEL_CHARGE_B", "420"), os.getenv("TRAVEL_CURRENCY_B", "EUR")),
        ],
        os.getenv("TRAVEL_SUPPLIER", "Example Hotel"),
    )
    print(json.dumps({"context": context(args.env), "triage": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
