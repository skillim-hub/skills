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
    business_name=os.getenv("HEBREW_COPYWRITER_BUSINESS_NAME", "א.א תיקוני מזגנים"),
    business_type=os.getenv("HEBREW_COPYWRITER_BUSINESS_TYPE", "טכנאי מזגנים"),
    offer=os.getenv("HEBREW_COPYWRITER_OFFER", "בדיקה ותיקון מזגנים"),
    audience=os.getenv("HEBREW_COPYWRITER_AUDIENCE", "משפחות ובעלי דירות"),
    channel=Channel.LANDING_PAGE,
    register=Register.DIRECT,
    price=Decimal(os.getenv("HEBREW_COPYWRITER_PRICE", "250")),
    include_vat=True,
    location=os.getenv("HEBREW_COPYWRITER_LOCATION", "חיפה"),
    proof_points=["מענה מהיר באזור חיפה", "חשבונית מס", "אחריות על התיקון"],
)
emit(args.env, HebrewCopywriterClient().generate_copy(brief))
