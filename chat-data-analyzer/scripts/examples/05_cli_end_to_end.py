from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the installed CLI on a sample dataset.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_ANALYZER_ENV", "sandbox"))
    parser.add_argument("--output", default=os.getenv("CHAT_ANALYZER_OUTPUT", "/tmp/chat-analyzer-cli-sample.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    subprocess.run([sys.executable, "-m", "chat_data_analyzer_cli", "sample", str(output_path)], check=True)
    completed = subprocess.run(
        [sys.executable, "-m", "chat_data_analyzer_cli", "analyze", str(output_path), "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    print(json.dumps({"env": args.env, "analysis": json.loads(completed.stdout)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
