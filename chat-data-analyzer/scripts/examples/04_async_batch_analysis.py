from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import asyncio

from chat_data_analyzer_client import AsyncChatDataAnalyzerClient, load_any, write_sample_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a dataset through the async client.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_ANALYZER_ENV", "sandbox"))
    parser.add_argument("--input", default=os.getenv("CHAT_ANALYZER_INPUT", ""))
    return parser.parse_args()


async def run(input_path: Path) -> dict:
    analyzer = AsyncChatDataAnalyzerClient()
    dataset = await analyzer.analyze_dataset(load_any(input_path))
    return {"conversation_count": dataset.conversation_count, "intent_distribution": dataset.intent_distribution}


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else Path(os.getenv("CHAT_ANALYZER_TMP", "/tmp")) / "chat-analyzer-async-sample.json"
    if not input_path.exists():
        write_sample_dataset(input_path)
    result = asyncio.run(run(input_path))
    print(json.dumps({"env": args.env, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
