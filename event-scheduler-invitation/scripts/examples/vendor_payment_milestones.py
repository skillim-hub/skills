from __future__ import annotations

import argparse
import json
import os

from event_scheduler_invitation import EventSchedulerClient, EventType, Guest, RSVPStatus, Vendor


def parse_env() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("EVENT_SCHEDULER_ENV", "sandbox"))
    return parser.parse_args()


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def main() -> None:
    args = parse_env()
    client = EventSchedulerClient()
    vendors = [
        Vendor("אולם", os.getenv("EVENT_SCHEDULER_VENUE_NAME", "גן אירועים"), 82500, deposit_nis=15000, contract_signed=True),
        Vendor("צילום", os.getenv("EVENT_SCHEDULER_PHOTO_VENDOR", "צלמת אירועים"), 9800, deposit_nis=2000, contract_signed=False),
        Vendor("תקליטן", os.getenv("EVENT_SCHEDULER_MUSIC_VENDOR", "תקליטן"), 6500, deposit_nis=1000, contract_signed=True),
    ]
    invoice_date = os.getenv("EVENT_SCHEDULER_INVOICE_DATE", "02/06/2026")
    print_json({
        "env": args.env,
        "schedule": client.vendor_payment_schedule(
            vendors,
            event_date=os.getenv("EVENT_SCHEDULER_EVENT_DATE", "18/06/2026"),
        ),
        "tax_checks": [
            client.tax_documentation_check(
                invoice_amount_before_vat_nis=vendor.quote_nis,
                invoice_date=invoice_date,
                vat_amount_nis=vendor.quote_nis * 0.18 if vendor.vat_included else None,
            )
            for vendor in vendors
        ],
        "music_license": client.music_license_checkpoint(
            event_type=os.getenv("EVENT_SCHEDULER_EVENT_TYPE", "wedding"),
            event_date=os.getenv("EVENT_SCHEDULER_EVENT_DATE", "18/06/2026"),
        ),
    })


if __name__ == "__main__":
    main()
