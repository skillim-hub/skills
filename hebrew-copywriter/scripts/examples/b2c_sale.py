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
    business_name=os.getenv("HEBREW_COPYWRITER_BUSINESS_NAME", "בית הקפה של רוני"),
    business_type=os.getenv("HEBREW_COPYWRITER_BUSINESS_TYPE", "בית קפה"),
    offer=os.getenv("HEBREW_COPYWRITER_OFFER", "מארז עוגיות לשישי"),
    audience=os.getenv("HEBREW_COPYWRITER_AUDIENCE", "לקוחות מהשכונה"),
    channel=Channel.WHATSAPP,
    register=Register.PLAYFUL,
    price=Decimal(os.getenv("HEBREW_COPYWRITER_PRICE", "69")),
    include_vat=True,
    deadline=os.getenv("HEBREW_COPYWRITER_DEADLINE", "30/06/2026"),
    include_unsubscribe=True,
    proof_points=["איסוף עצמי עד 14:00", "כמות מוגבלת לפי מלאי יומי"],
)
emit(args.env, HebrewCopywriterClient().generate_copy(brief))
