#!/usr/bin/env python3
"""Export monitored updates to JSON."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from regulatory_update_notifier import RegulatoryMonitorClient, default_sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RUN_ENV", "sandbox"))
    parser.add_argument("--output", default=os.getenv("OUTPUT_PATH", "updates.json"))
    args = parser.parse_args()

    updates = RegulatoryMonitorClient(default_sources(args.env)).collect_updates(limit=int(os.getenv("LIMIT", "10")))
    payload = [item.to_dict() for item in updates]
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": args.output, "count": len(payload)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
