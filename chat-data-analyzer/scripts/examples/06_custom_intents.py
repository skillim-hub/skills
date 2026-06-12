from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from chat_data_analyzer_client import ChatDataAnalyzerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a message with custom intent terms.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_ANALYZER_ENV", "sandbox"))
    parser.add_argument("--text", default=os.getenv("CHAT_ANALYZER_TEXT", "יש בעיה במנוי הפרימיום"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analyzer = ChatDataAnalyzerClient(custom_intents={"subscription": ["מנוי", "פרימיום", "חידוש"]})
    result = analyzer.analyze_text(args.text)
    print(json.dumps({"env": args.env, "analysis": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
