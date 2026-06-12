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
    prop = client.create_property("הרצל 10", "חיפה", "4")
    tenant = client.add_tenant(prop["id"], os.getenv("PMS_TENANT_NAME", "דנה כהן"), email=os.getenv("PMS_TENANT_EMAIL", "dana@example.com"))
    lease = client.create_lease(prop["id"], tenant["id"], "01/01/2026", "31/12/2026", os.getenv("PMS_RENT_ILS", "5200"), due_day=5)
    charges = client.schedule_rent(lease["id"], "01/01/2026", months=3)
    message = client.generate_tenant_message("rent_reminder", charge_id=charges[0]["id"])
    emit({"property": prop, "tenant": tenant, "lease": lease, "charges": charges, "message": message})


if __name__ == "__main__":
    main()
