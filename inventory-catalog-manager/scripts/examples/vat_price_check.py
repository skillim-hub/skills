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
    parser = argparse.ArgumentParser(description="Check VAT-inclusive and before-VAT prices.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ICM_ENV", "sandbox"))
    parser.add_argument("--price", default=os.getenv("ICM_PRICE", "100"))
    parser.add_argument("--vat-rate", default=os.getenv("ICM_VAT_RATE", "0.18"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = {
        "env": args.env,
        "price_with_vat": args.price,
        "vat_rate": args.vat_rate,
        "before_vat": str(client.calculate_price_before_vat(args.price, args.vat_rate)),
        "price_before_vat_42_37_with_vat": str(client.calculate_price_with_vat("42.37", args.vat_rate)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
