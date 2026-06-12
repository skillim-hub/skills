from __future__ import annotations

import argparse
import json
import os

import customer_feedback_collector as C


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Create a Zap SMS review request after delivery.')
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CFC_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    business = C.BusinessProfile(
        display_name=os.getenv("CFC_BUSINESS_NAME", "החנות של מיכל"),
        city=os.getenv("CFC_CITY", "חולון"),
        zap_url=os.getenv("CFC_ZAP_URL", "https://www.zap.co.il/clientcard.aspx?siteid=12345"),
    )
    customer = C.Contact(
        full_name=os.getenv("CFC_CUSTOMER_NAME", "יואב לוי"),
        phone=os.getenv("CFC_CUSTOMER_PHONE", "052-222-3344"),
        email=os.getenv("CFC_CUSTOMER_EMAIL", "yoav@example.co.il"),
        consent=os.getenv("CFC_CONSENT", "true").lower() == "true",
        consent_basis=C.ConsentBasis.TRANSACTION_FOLLOWUP,
        tags=("delivered", "order-249-ils"),
    )
    message = C.render_message(customer, business, platform=C.ReviewPlatform.ZAP, channel=C.Channel.SMS)
    print(json.dumps({"env": args.env, "message": C.to_jsonable(message)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
