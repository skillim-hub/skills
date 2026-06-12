from __future__ import annotations

import argparse
import json
import os

import customer_feedback_collector as C


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Build a feedback campaign plan from CSV data.')
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CFC_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    business = C.BusinessProfile(
        display_name=os.getenv("CFC_BUSINESS_NAME", "קליניקת הדר"),
        google_place_id=os.getenv("CFC_GOOGLE_PLACE_ID", "ChIJexample"),
        private_feedback_url=os.getenv("CFC_PRIVATE_FEEDBACK_URL", "https://clinic.example.co.il/private"),
    )
    customer = C.Contact(
        full_name=os.getenv("CFC_CUSTOMER_NAME", "דנה כהן"),
        phone=os.getenv("CFC_CUSTOMER_PHONE", "0501234567"),
        email=os.getenv("CFC_CUSTOMER_EMAIL", "dana@example.co.il"),
        consent=os.getenv("CFC_CONSENT", "true").lower() == "true",
        preferred_channel=C.Channel.WHATSAPP,
        rating=5,
    )
    second = C.Contact(
        full_name=os.getenv("CFC_SECOND_CUSTOMER_NAME", "יוסי לוי"),
        phone=os.getenv("CFC_SECOND_CUSTOMER_PHONE", "0522223344"),
        email=os.getenv("CFC_SECOND_CUSTOMER_EMAIL", "yossi@example.co.il"),
        consent=True,
        preferred_channel=C.Channel.SMS,
        rating=5,
    )
    plan = C.plan_campaign([customer, second], business, platform=C.ReviewPlatform.GOOGLE)
    print(json.dumps({"env": args.env, "summary": C.summarize_plan(plan), "items": C.to_jsonable(plan)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
