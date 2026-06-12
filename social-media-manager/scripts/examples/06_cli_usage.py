#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("SOCIAL_MEDIA_MANAGER_ENV", "sandbox"))
    parser.add_argument("--caption", default=os.getenv("SOCIAL_MEDIA_MANAGER_CAPTION", "טיפ קצר לבעלי עסקים"))
    args = parser.parse_args()
    cli_path = Path(__file__).resolve().parents[1] / "social-media-manager-cli.py"
    result = subprocess.run([sys.executable, str(cli_path), "validate", "--env", args.env, "--platform", "instagram", "--format", "reel", "--media-count", "1", "--caption", args.caption, "--hashtag", "#עסקים קטנים"], text=True, capture_output=True, check=False)
    payload = {"environment": args.env, "scenario": "cli_usage", "returncode": result.returncode, "stdout": json.loads(result.stdout), "stderr": result.stderr}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
