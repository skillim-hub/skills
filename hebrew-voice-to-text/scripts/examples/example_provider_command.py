"""Run a provider command from environment configuration."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from hebrew_voice_to_text import HebrewVoiceTextClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HVTT_ENV", "sandbox"))
    parser.add_argument("--input", default=os.getenv("HVTT_AUDIO_FILE", "sample.wav"))
    parser.add_argument("--provider-command", default=os.getenv("HVTT_PROVIDER_COMMAND"))
    args = parser.parse_args()

    client = HebrewVoiceTextClient(provider_command=args.provider_command, env=args.env)
    input_path = Path(args.input)
    if args.provider_command:
        result = client.transcribe(input_path)
        payload = client.summarize_result(result)
    else:
        payload = {
            "env": args.env,
            "status": "provider_command_missing",
            "set": "HVTT_PROVIDER_COMMAND",
            "example": "python provider.py {input} {language}",
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
