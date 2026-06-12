from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from hebrew_translation_assistant import HebrewTranslationAssistant


def parser(description: str) -> argparse.ArgumentParser:
    item = argparse.ArgumentParser(description=description)
    item.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HEBREW_TRANSLATION_ASSISTANT_ENV", "sandbox"))
    item.add_argument("--home", default=os.getenv("HEBREW_TRANSLATION_ASSISTANT_HOME"))
    return item


def client_from_args(args: argparse.Namespace) -> HebrewTranslationAssistant:
    return HebrewTranslationAssistant(storage_dir=Path(args.home) if args.home else None)


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
