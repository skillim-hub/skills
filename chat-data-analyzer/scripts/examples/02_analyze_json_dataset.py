from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from chat_data_analyzer_client import ChatDataAnalyzerClient, load_any, write_sample_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a JSON, JSONL, or CSV dataset.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_ANALYZER_ENV", "sandbox"))
    parser.add_argument("--input", default=os.getenv("CHAT_ANALYZER_INPUT", ""))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else Path(os.getenv("CHAT_ANALYZER_TMP", "/tmp")) / "chat-analyzer-sample.json"
    if not input_path.exists():
        write_sample_dataset(input_path)
    analyzer = ChatDataAnalyzerClient()
    dataset = analyzer.analyze_dataset(load_any(input_path))
    print(json.dumps({"env": args.env, "dataset": json.loads(analyzer.to_json(dataset))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
