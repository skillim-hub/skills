#!/usr/bin/env python3
"""Batch CSV qualification example."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from lead_qualification_bot import LeadQualificationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LQB_ENV", "sandbox"))
    parser.add_argument("--input", default=os.getenv("LQB_INPUT", str(Path(__file__).with_name("sample_leads.csv"))))
    parser.add_argument("--output", default=os.getenv("LQB_OUTPUT", str(Path(__file__).with_name("qualified_sample_leads.csv"))))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = LeadQualificationClient(environment=args.env)
    leads = client.batch_csv(args.input, args.output)
    payload = {
        "environment": args.env,
        "input": args.input,
        "output": args.output,
        "count": len(leads),
        "lead_ids": [lead.lead_id for lead in leads],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
