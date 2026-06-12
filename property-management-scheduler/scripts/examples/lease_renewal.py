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
    prop = client.create_property("בן גוריון 22", "רמת גן", "9")
    tenant = client.add_tenant(prop["id"], os.getenv("PMS_TENANT_NAME", "אורי לוי"), phone=os.getenv("PMS_TENANT_PHONE", "0501234567"), preferred_channel="sms")
    message = client.generate_tenant_message("lease_renewal", tenant_id=tenant["id"])
    log = client.log_communication(tenant["id"], prop["id"], "sms", message["subject"], message["body"], scheduled_for=os.getenv("PMS_SCHEDULED_FOR", "20/11/2026"))
    emit({"message": message, "communication": log})


if __name__ == "__main__":
    main()
