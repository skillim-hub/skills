from __future__ import annotations

import argparse
import json
import os

try:
    import inventory_catalog_manager_client as client
except ModuleNotFoundError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    import inventory_catalog_manager_client as client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconcile a physical stock count.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICM_ENV", "sandbox"))
    parser.add_argument("--counted", default=os.getenv("ICM_COUNTED_QUANTITY", "16"))
    parser.add_argument("--reference", default=os.getenv("ICM_COUNT_REFERENCE", "COUNT-02-06-2026"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = client.InventoryCatalog(items=[
        client.CatalogItem(
            sku="COF-BNS-001",
            name="פולי קפה 1 ק״ג",
            unit="kg",
            price_before_vat="42.37",
            vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
            stock_quantity="18",
            reorder_point="5",
        )
    ])
    movement = catalog.set_stock_from_count(
        "COF-BNS-001",
        args.counted,
        reference=args.reference,
        note="Physical count reconciliation",
    )
    payload = {
        "env": args.env,
        "movement": movement.to_dict() if movement else None,
        "current_quantity": catalog.get_item("COF-BNS-001").stock_quantity,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
