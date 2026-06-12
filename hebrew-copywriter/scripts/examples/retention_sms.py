from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal

from hebrew_copywriter import Channel, CopyBrief, HebrewCopywriterClient, Register


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HEBREW_COPYWRITER_ENV", "sandbox"))
    return p


def emit(env: str, result: dict) -> None:
    payload = {"env": env, "result": result}
    print(json.dumps(payload, ensure_ascii=False, indent=2))

args = parser().parse_args()
brief = CopyBrief(
    business_name=os.getenv("HEBREW_COPYWRITER_BUSINESS_NAME", "מספרת דנה"),
    business_type=os.getenv("HEBREW_COPYWRITER_BUSINESS_TYPE", "מספרה"),
    offer=os.getenv("HEBREW_COPYWRITER_OFFER", "תור לצבע לפני החג"),
    audience=os.getenv("HEBREW_COPYWRITER_AUDIENCE", "לקוחות קיימים"),
    channel=Channel.SMS,
    deadline=os.getenv("HEBREW_COPYWRITER_DEADLINE", "09/09/2026"),
    include_unsubscribe=True,
)
emit(args.env, HebrewCopywriterClient().generate_copy(brief))
