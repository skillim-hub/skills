from __future__ import annotations

import argparse
import json
import os

import customer_feedback_collector as C


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Create a Google WhatsApp review request after an appointment.')
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CFC_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    business = C.BusinessProfile(
        display_name=os.getenv("CFC_BUSINESS_NAME", "קליניקת הדר"),
        city=os.getenv("CFC_CITY", "רמת גן"),
        google_place_id=os.getenv("CFC_GOOGLE_PLACE_ID", "ChIJexample"),
        private_feedback_url=os.getenv("CFC_PRIVATE_FEEDBACK_URL", "https://clinic.example.co.il/feedback"),
    )
    customer = C.Contact(
        full_name=os.getenv("CFC_CUSTOMER_NAME", "דנה כהן"),
        phone=os.getenv("CFC_CUSTOMER_PHONE", "050-123-4567"),
        email=os.getenv("CFC_CUSTOMER_EMAIL", "dana@example.co.il"),
        consent=os.getenv("CFC_CONSENT", "true").lower() == "true",
        consent_basis=C.ConsentBasis.TRANSACTION_FOLLOWUP,
        tags=("appointment-complete",),
    )
    message = C.render_message(customer, business, platform=C.ReviewPlatform.GOOGLE, channel=C.Channel.WHATSAPP)
    print(json.dumps({"env": args.env, "message": C.to_jsonable(message)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
