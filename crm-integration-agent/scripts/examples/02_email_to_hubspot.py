from __future__ import annotations

import argparse
import json
import os

from crm_integration_agent import CRMIntegrationClient, Contact, ConversationMessage, ConversationThread, ConsentRecord, result_to_dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CRM_ENV", "sandbox"))
    return parser.parse_args()


args = parse_args()
thread = ConversationThread(
    source_channel="email",
    source_thread_id=os.getenv("EMAIL_THREAD_ID", "mail-2026-02-18-1"),
    subject="חשבונית מס וקבלה",
    contact=Contact(full_name="אמיר לוי", email=os.getenv("CUSTOMER_EMAIL", "amir@example.co.il"), company="לוי שירותים"),
    messages=[ConversationMessage("mail-1", "18/02/2026 11:10:00", "inbound", "נא לשלוח חשבונית מס וקבלה על ₪780")],
    consent=ConsentRecord(marketing_opt_in=False, evidence="טיפול שירותי לאחר רכישה"),
    business_purpose="admin",
)
client = CRMIntegrationClient.from_env("hubspot", environment=args.env, dry_run=args.env == "sandbox")
result = client.sync_thread(thread)
print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
