#!/usr/bin/env python3
"""B2B tax invoice scenario that crosses the allocation threshold."""

from __future__ import annotations

import argparse
import json
import os

from invoice_generator import DocumentSpec, ShaamClient, sample_tax_invoice


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_GENERATOR_ENV", "sandbox"))
    parser.add_argument("--request-allocation", action="store_true")
    args = parser.parse_args()

    spec = DocumentSpec.from_dict(sample_tax_invoice())
    result = {
        "environment": args.env,
        "base_url": os.getenv(f"SHAAM_{args.env.upper()}_BASE_URL", ""),
        "allocation_required": spec.requires_allocation(),
        "payload": spec.to_shaam_payload(),
    }
    if args.request_allocation:
        token = os.getenv("SHAAM_ACCESS_TOKEN", "")
        base_url = result["base_url"]
        if not token or not base_url:
            raise SystemExit("Set SHAAM_ACCESS_TOKEN and SHAAM_<ENV>_BASE_URL before live allocation requests")
        result["allocation_response"] = ShaamClient(base_url, token).request_allocation(spec)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
