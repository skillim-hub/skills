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
    parser = argparse.ArgumentParser(description="Create a service catalog for a freelancer.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICM_ENV", "sandbox"))
    parser.add_argument("--hourly-rate", default=os.getenv("ICM_HOURLY_RATE", "350"))
    parser.add_argument("--project-rate", default=os.getenv("ICM_PROJECT_RATE", "1800"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = client.InventoryCatalog()
    catalog.add_item(client.CatalogItem(
        sku="SRV-CONS-001",
        name="פגישת ייעוץ",
        name_en="Consulting session",
        unit="hour",
        category="services",
        price_before_vat=args.hourly_rate,
        vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
        stock_quantity="0",
        reorder_point="0",
    ))
    catalog.add_item(client.CatalogItem(
        sku="SRV-SETUP-001",
        name="הקמת מערכת",
        name_en="Setup project",
        unit="project",
        category="services",
        price_before_vat=args.project_rate,
        vat_rate=os.getenv("ICM_VAT_RATE", "0.18"),
        stock_quantity="0",
        reorder_point="0",
    ))
    payload = {"env": args.env, "b2b_rows": client.b2b_export_rows(catalog)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
