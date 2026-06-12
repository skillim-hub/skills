#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os

from social_media_manager_client import SocialMediaManagerClient, sample_drafts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("SOCIAL_MEDIA_MANAGER_ENV", "sandbox"))
    parser.add_argument("--start-date", default=os.getenv("SOCIAL_MEDIA_MANAGER_START_DATE", "2026-06-08"))
    parser.add_argument("--business-type", default=os.getenv("SOCIAL_MEDIA_MANAGER_BUSINESS_TYPE", "קונדיטוריה"))
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    client = SocialMediaManagerClient()
    posts = await client.async_schedule_posts(sample_drafts(["tiktok", "instagram"], business_type=args.business_type), start_date=args.start_date, days=7)
    print(json.dumps({"environment": args.env, "scenario": "async_schedule", "items": [post.to_dict() for post in posts]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
