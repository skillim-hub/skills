#!/usr/bin/env python3
"""Run the async collector and print JSON output."""

from __future__ import annotations

import argparse
import asyncio
import json
import os

from regulatory_update_notifier import RegulatoryMonitorClient, create_profile, default_sources


async def run(env: str) -> None:
    profile = create_profile(
        name=os.getenv("PROFILE_NAME", "בדיקה אסינכרונית"),
        industries=os.getenv("INDUSTRIES", "ecommerce,privacy").split(","),
        keywords=os.getenv("KEYWORDS", "מאגר מידע,cancellation").split(","),
        locale=os.getenv("LOCALE", "he"),
        environment=env,
    )
    updates = await RegulatoryMonitorClient(default_sources(env)).acollect_updates(profile=profile)
    print(json.dumps({"profile": profile.to_dict(), "updates": [item.to_dict() for item in updates]}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RUN_ENV", "sandbox"))
    args = parser.parse_args()
    asyncio.run(run(args.env))


if __name__ == "__main__":
    main()
