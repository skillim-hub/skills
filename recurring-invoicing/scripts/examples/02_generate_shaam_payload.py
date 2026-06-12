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
    config = env_config(args.env)
    subscription = Subscription(
        subscription_id="SUB-IL-ALLOC",
        customer=Customer(name="Acme Israel", tax_id="514324995"),
        line_items=[LineItem(description="Annual software license", quantity="1", unit_price="20000.00")],
        start_date=date(2026, 2, 1),
    )
    invoice = build_invoice(subscription, date(2026, 2, 1), 1)
    payload = create_shaam_allocation_payload(
        AllocationRequest(
            environment=args.env,
            business_tax_id=str(config["business_tax_id"]),
            invoice=invoice,
            client_transaction_id="TX-ALLOC-001",
            software_id=config["software_id"],
        )
    )
    print_json(payload)


if __name__ == "__main__":
    main()
