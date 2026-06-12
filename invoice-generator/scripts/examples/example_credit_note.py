#!/usr/bin/env python3
"""Credit note against an allocated tax invoice."""

from __future__ import annotations

import argparse
import json
import os

from invoice_generator import DocumentSpec, sample_credit_note


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_GENERATOR_ENV", "sandbox"))
    args = parser.parse_args()

    spec = DocumentSpec.from_dict(sample_credit_note())
    output = {"environment": args.env, "validation": spec.validate().to_dict(), "totals": spec.calculate_totals().to_dict(), "payload": spec.to_shaam_payload()}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
