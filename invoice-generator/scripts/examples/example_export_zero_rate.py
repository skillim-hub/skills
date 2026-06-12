#!/usr/bin/env python3
"""Foreign customer zero-rate export scenario."""

from __future__ import annotations

import argparse
import json
import os

from invoice_generator import DocumentSpec, sample_export_zero_rate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_GENERATOR_ENV", "sandbox"))
    args = parser.parse_args()

    spec = DocumentSpec.from_dict(sample_export_zero_rate())
    output = {"environment": args.env, "validation": spec.validate().to_dict(), "totals": spec.calculate_totals().to_dict(), "allocation_required": spec.requires_allocation()}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
