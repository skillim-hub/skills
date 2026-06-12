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
    prop = client.create_property(
        address=os.getenv("PMS_PROPERTY_ADDRESS", "הירקון 12"),
        city=os.getenv("PMS_PROPERTY_CITY", "תל אביב-יפו"),
        apartment=os.getenv("PMS_PROPERTY_APARTMENT", "דירה 8"),
        arnona_account=os.getenv("PMS_ARNONA_ACCOUNT", ""),
    )
    emit(prop)


if __name__ == "__main__":
    main()
