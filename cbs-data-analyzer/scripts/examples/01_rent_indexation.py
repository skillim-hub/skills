from __future__ import annotations

import argparse
import json
import os

import cbs_data_analyzer_client as cbs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate a rent or contract indexation scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CBS_ENV", "sandbox"))
    parser.add_argument("--amount", type=float, default=float(os.getenv("CBS_EXAMPLE_AMOUNT", "5200")))
    parser.add_argument("--base-index", type=float, default=float(os.getenv("CBS_EXAMPLE_BASE_INDEX", "103.1")))
    parser.add_argument("--target-index", type=float, default=float(os.getenv("CBS_EXAMPLE_TARGET_INDEX", "106.4")))
    parser.add_argument("--floor-zero", action="store_true", default=os.getenv("CBS_EXAMPLE_FLOOR_ZERO") == "1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = cbs.calculate_indexation(
        original_amount=args.amount,
        base_index=args.base_index,
        target_index=args.target_index,
        floor_zero=args.floor_zero,
    )
    payload = {"environment": args.env, "scenario": "rent_indexation", "result": result.to_dict()}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
