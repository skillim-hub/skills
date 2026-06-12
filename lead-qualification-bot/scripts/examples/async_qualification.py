#!/usr/bin/env python3
"""Project qualification example."""

from __future__ import annotations

import argparse
import json
import os

from lead_qualification_bot import LeadQualificationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LQB_ENV", "sandbox"))
    parser.add_argument("--phone", default=os.getenv("LQB_PHONE", "050-123-4567"))
    parser.add_argument("--name", default=os.getenv("LQB_NAME", "יואב"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = LeadQualificationClient(environment=args.env)
    lead = client.create_lead(message=os.getenv("LQB_MESSAGE", "צריך אתר תדמית עד סוף החודש תקציב 6000 שח"), phone=args.phone, name=args.name)
    print(json.dumps(client.to_dict(lead), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
