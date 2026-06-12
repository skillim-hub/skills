from __future__ import annotations

import argparse
import json
import os

import customer_feedback_collector as C


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Create an email testimonial approval request.')
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CFC_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    business = C.BusinessProfile(
        display_name=os.getenv("CFC_BUSINESS_NAME", "סטודיו נועה"),
        city=os.getenv("CFC_CITY", "תל אביב"),
        custom_review_url=os.getenv("CFC_CUSTOM_REVIEW_URL", "https://studio.example.co.il/testimonial-approval"),
    )
    customer = C.Contact(
        full_name=os.getenv("CFC_CUSTOMER_NAME", "רונית אברהם"),
        phone=os.getenv("CFC_CUSTOMER_PHONE", "050-111-2222"),
        email=os.getenv("CFC_CUSTOMER_EMAIL", "ronit@example.co.il"),
        consent=os.getenv("CFC_CONSENT", "true").lower() == "true",
        consent_basis=C.ConsentBasis.EXPLICIT_OPT_IN,
        tags=("project-complete",),
    )
    message = C.render_message(customer, business, platform=C.ReviewPlatform.CUSTOM, channel=C.Channel.EMAIL)
    print(json.dumps({"env": args.env, "message": C.to_jsonable(message)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
