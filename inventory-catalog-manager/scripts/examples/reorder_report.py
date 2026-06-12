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
    parser = argparse.ArgumentParser(description="Generate a reorder report.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICM_ENV", "sandbox"))
    parser.add_argument("--supplier", default=os.getenv("ICM_SUPPLIER_NAME", "Ceramics Supplier"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = client.InventoryCatalog(items=[
        client.CatalogItem(
            sku="MUG-WHT-001",
            name="ספל לבן",
            unit="unit",
            price_before_vat="21.19",
            vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
            stock_quantity="6",
            reorder_point="8",
            supplier_name=args.supplier,
        ),
        client.CatalogItem(
            sku="COF-BNS-001",
            name="פולי קפה 1 ק״ג",
            unit="kg",
            price_before_vat="42.37",
            vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
            stock_quantity="18",
            reorder_point="5",
            supplier_name="Roaster",
        ),
    ])
    payload = {"env": args.env, "low_stock": [item.to_dict() for item in catalog.low_stock()]}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
