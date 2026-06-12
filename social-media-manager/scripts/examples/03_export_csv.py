#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from social_media_manager_client import BlackoutPeriod, PostDraft, SocialMediaManagerClient, sample_drafts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("SOCIAL_MEDIA_MANAGER_ENV", "sandbox"))
    parser.add_argument("--start-date", default=os.getenv("SOCIAL_MEDIA_MANAGER_START_DATE", "2026-06-08"))
    parser.add_argument("--business-type", default=os.getenv("SOCIAL_MEDIA_MANAGER_BUSINESS_TYPE", "עסק מקומי"))
    return parser.parse_args()


def dump(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    client = SocialMediaManagerClient()
    posts = client.schedule_posts(sample_drafts(["facebook", "linkedin"], business_type=args.business_type), start_date=args.start_date, days=10)
    dump({"environment": args.env, "scenario": "export_csv", "csv": client.export_csv(posts)})


if __name__ == "__main__":
    main()
