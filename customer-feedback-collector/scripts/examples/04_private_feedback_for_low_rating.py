from __future__ import annotations

import argparse
import json
import os

import customer_feedback_collector as C


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Route a low rating to private service recovery.')
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CFC_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    business = C.BusinessProfile(
        display_name=os.getenv("CFC_BUSINESS_NAME", "מוסך ארז"),
        city=os.getenv("CFC_CITY", "פתח תקווה"),
        google_place_id=os.getenv("CFC_GOOGLE_PLACE_ID", "ChIJgarage"),
        private_feedback_url=os.getenv("CFC_PRIVATE_FEEDBACK_URL", "https://garage.example.co.il/service-recovery"),
    )
    customer = C.Contact(
        full_name=os.getenv("CFC_CUSTOMER_NAME", "אורי ישראלי"),
        phone=os.getenv("CFC_CUSTOMER_PHONE", "054-555-1212"),
        email=os.getenv("CFC_CUSTOMER_EMAIL", "ori@example.co.il"),
        consent=os.getenv("CFC_CONSENT", "true").lower() == "true",
        consent_basis=C.ConsentBasis.TRANSACTION_FOLLOWUP,
        rating=int(os.getenv("CFC_CUSTOMER_RATING", "2")),
    )
    message = C.render_message(customer, business, platform=C.ReviewPlatform.GOOGLE, channel=C.Channel.WHATSAPP)
    print(json.dumps({"env": args.env, "message": C.to_jsonable(message)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
