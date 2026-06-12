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
    parser = argparse.ArgumentParser(description="Import and export catalog CSV.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICM_ENV", "sandbox"))
    parser.add_argument("--csv-path", default=os.getenv("ICM_SOURCE_CSV", ""))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with TemporaryDirectory() as tmp:
        csv_path = Path(args.csv_path) if args.csv_path else Path(tmp) / "source.csv"
        out_path = Path(tmp) / "out.csv"
        if not args.csv_path:
            csv_path.write_text(
                "sku,name,unit,price_before_vat,vat_rate,stock_quantity,reorder_point\n"
                "MUG-WHT-001,ספל לבן,unit,21.19,0.18,34,8\n",
                encoding="utf-8",
            )
        catalog = client.InventoryCatalog.import_csv(csv_path)
        catalog.export_csv(out_path, utf8_bom=True)
        payload = {
            "env": args.env,
            "source": str(csv_path),
            "export": str(out_path),
            "price_with_vat": catalog.get_item("MUG-WHT-001").price_with_vat,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
