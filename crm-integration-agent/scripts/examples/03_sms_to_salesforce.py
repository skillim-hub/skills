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
    source_channel="sms",
    source_thread_id=os.getenv("SMS_THREAD_ID", "sms-77"),
    subject="תיאום פגישה",
    contact=Contact(full_name="נועה ישראלי", phone=os.getenv("CUSTOMER_PHONE", "052-222-3333"), company="ישראלי ייעוץ"),
    messages=[ConversationMessage("sms-77-1", "19/02/2026 08:30:00", "inbound", "אפשר לקבוע פגישה ביום חמישי?")],
    consent=ConsentRecord(marketing_opt_in=False, evidence="בקשת שירות במסרון"),
    business_purpose="appointment",
)
client = CRMIntegrationClient.from_env("salesforce", environment=args.env, dry_run=args.env == "sandbox", base_url=os.getenv("SALESFORCE_BASE_URL", "https://example.my.salesforce.com"))
result = client.sync_thread(thread)
print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
