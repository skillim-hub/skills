from __future__ import annotations

import argparse
import json
import os
from datetime import date

from recurring_invoicing import (
    AllocationRequest,
    Customer,
    Interval,
    LineItem,
    RecurringInvoicingClient,
    Subscription,
    build_invoice,
    create_shaam_allocation_payload,
    credit_note_for_invoice,
    vat_rate_for_issue_date,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RECURRING_INVOICING_ENV", "sandbox"))
    return parser.parse_args()


def env_config(environment: str) -> dict[str, str | None]:
    suffix = environment.upper()
    return {
        "environment": environment,
        "business_tax_id": os.getenv("BUSINESS_TAX_ID", "000000018"),
        "shaam_client_id": os.getenv("SHAAM_CLIENT_ID"),
        "shaam_client_secret": os.getenv("SHAAM_CLIENT_SECRET"),
        "shaam_base_url": os.getenv(f"SHAAM_BASE_URL_{suffix}", os.getenv("SHAAM_BASE_URL")),
        "software_id": os.getenv("SHAAM_SOFTWARE_ID", "demo-software"),
    }


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> None:
    args = parse_args()
    subscription = Subscription(
        subscription_id="SUB-CREDIT-001",
        customer=Customer(name="Credit Example Ltd", tax_id="514324995"),
        line_items=[LineItem(description="Consulting retainer", quantity="1", unit_price="1500.00")],
        start_date=date(2026, 4, 1),
    )
    invoice = build_invoice(subscription, date(2026, 4, 1), 1)
    credit = credit_note_for_invoice(invoice, "Service cancelled before delivery", 1)
    print_json({"environment": args.env, "invoice": invoice.to_dict(), "credit_note": credit.to_dict()})


if __name__ == "__main__":
    main()
