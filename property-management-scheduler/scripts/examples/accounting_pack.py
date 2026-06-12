from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from property_management_scheduler import PropertyManagementScheduler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PMS_ENV", "sandbox"))
    parser.add_argument("--store", default=os.getenv("PMS_STORE_PATH", str(Path(os.getenv("PMS_DATA_DIR", "/tmp")) / "pms-example.json")))
    return parser.parse_args()


def client_from_args(args: argparse.Namespace) -> PropertyManagementScheduler:
    return PropertyManagementScheduler(store_path=args.store, environment=args.env)


def emit(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))



def main() -> None:
    args = parse_args()
    client = client_from_args(args)
    prop = client.create_property("יפו 3", "ירושלים", "1")
    tenant = client.add_tenant(prop["id"], "נועה ישראלי", email=os.getenv("PMS_TENANT_EMAIL", "noa@example.com"))
    lease = client.create_lease(prop["id"], tenant["id"], "01/01/2026", "31/12/2026", "4700")
    charge = client.schedule_rent(lease["id"], "01/01/2026", months=1)[0]
    client.record_payment(charge["id"], "02/01/2026", "4700", reference=os.getenv("PMS_PAYMENT_REFERENCE", "bank-2026-001"))
    emit(client.export_accounting_pack("01/01/2026", "31/01/2026"))


if __name__ == "__main__":
    main()
