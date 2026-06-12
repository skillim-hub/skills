from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from chat_data_analyzer_client import ChatDataAnalyzerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze one customer message.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_ANALYZER_ENV", "sandbox"))
    parser.add_argument("--text", default=os.getenv("CHAT_ANALYZER_TEXT", "המשלוח לא הגיע ואני רוצה החזר דחוף"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analyzer = ChatDataAnalyzerClient()
    result = analyzer.analyze_text(args.text)
    print(json.dumps({"env": args.env, "analysis": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
