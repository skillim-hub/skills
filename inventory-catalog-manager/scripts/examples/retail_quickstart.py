from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    import inventory_catalog_manager_client as client
except ModuleNotFoundError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    import inventory_catalog_manager_client as client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a small retail catalog.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICM_ENV", "sandbox"))
    parser.add_argument("--catalog-path", default=os.getenv("ICM_CATALOG_PATH", ""))
    return parser.parse_args()


def build_catalog() -> client.InventoryCatalog:
    catalog = client.InventoryCatalog()
    catalog.add_item(client.CatalogItem(
        sku="COF-BNS-001",
        name="פולי קפה 1 ק״ג",
        unit="kg",
        category="coffee",
        price_before_vat=os.getenv("ICM_COFFEE_PRICE_BEFORE_VAT", "42.37"),
        vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
        stock_quantity=os.getenv("ICM_COFFEE_STOCK", "18"),
        reorder_point="5",
    ))
    catalog.add_item(client.CatalogItem(
        sku="MUG-WHT-001",
        name="ספל לבן",
        unit="unit",
        category="accessories",
        price_before_vat="21.19",
        vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
        stock_quantity="34",
        reorder_point="8",
    ))
    return catalog


def main() -> None:
    args = parse_args()
    catalog = build_catalog()
    if args.catalog_path:
        path = Path(args.catalog_path)
        catalog.save_json(path)
        output_path = path
    else:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "catalog.json"
            catalog.save_json(output_path)
            payload = {"env": args.env, "path": str(output_path), "low_stock": [i.to_dict() for i in catalog.low_stock()]}
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return
    payload = {"env": args.env, "path": str(output_path), "items": [i.to_dict() for i in catalog.list_items()]}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
