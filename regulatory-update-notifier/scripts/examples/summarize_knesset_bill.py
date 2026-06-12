#!/usr/bin/env python3
"""Summarize bill-like records from the configured environment."""

from __future__ import annotations

import argparse
import json
import os

from regulatory_update_notifier import RegulatoryMonitorClient, default_sources, summarize_update


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RUN_ENV", "sandbox"))
    parser.add_argument("--locale", default=os.getenv("LOCALE", "he"))
    args = parser.parse_args()

    updates = RegulatoryMonitorClient(default_sources(args.env)).collect_updates(keywords=os.getenv("KEYWORDS", "הצעת חוק,bill").split(","))
    summaries = [summarize_update(item, locale=args.locale) for item in updates if item.status in {"bill", "draft-regulation"}]
    print(json.dumps({"summaries": summaries}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
