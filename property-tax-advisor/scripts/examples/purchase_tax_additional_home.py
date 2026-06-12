from __future__ import annotations

import argparse
import json
import os

from property_tax_advisor import estimate_purchase_tax


def main() -> None:
    parser = argparse.ArgumentParser(description="Additional-home purchase tax scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PTA_ENV", "sandbox"))
    args = parser.parse_args()
    result = estimate_purchase_tax(
        price=float(os.getenv("PTA_PRICE", "2400000")),
        buyer_profile=os.getenv("PTA_BUYER_PROFILE", "additional_home"),
        contract_date=os.getenv("PTA_CONTRACT_DATE", "15/03/2026"),
    )
    print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
