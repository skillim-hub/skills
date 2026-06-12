#!/usr/bin/env python3
"""Build a Hebrew consumer-rights digest from monitored sources."""

from __future__ import annotations

import argparse
import json
import os

from regulatory_update_notifier import RegulatoryMonitorClient, create_profile, default_sources, make_digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RUN_ENV", "sandbox"))
    args = parser.parse_args()

    profile = create_profile(
        name=os.getenv("PROFILE_NAME", "צרכנים"),
        industries=["consumers"],
        keywords=os.getenv("KEYWORDS", "ביטול עסקה,צרכנות").split(","),
        locale=os.getenv("LOCALE", "he"),
        environment=args.env,
    )
    updates = RegulatoryMonitorClient(default_sources(args.env)).collect_updates(profile=profile)
    print(json.dumps({"digest": make_digest(updates, locale=profile.locale)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
