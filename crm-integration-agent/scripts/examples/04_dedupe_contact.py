from __future__ import annotations

import argparse
import json
import os

from crm_integration_agent import Contact, build_dedupe_key, canonical_email, normalize_israeli_phone

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CRM_ENV", "sandbox"))
args = parser.parse_args()
contact = Contact(full_name=os.getenv("CUSTOMER_NAME", "דנה כהן"), phone=os.getenv("CUSTOMER_PHONE", "0501234567"), email=os.getenv("CUSTOMER_EMAIL", "dana@example.co.il"))
payload = {
    "environment": args.env,
    "phone": normalize_israeli_phone(contact.phone),
    "email": canonical_email(contact.email),
    "dedupe_key": build_dedupe_key(contact),
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
