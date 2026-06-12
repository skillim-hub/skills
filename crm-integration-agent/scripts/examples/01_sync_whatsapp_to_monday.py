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
    source_channel="whatsapp",
    source_thread_id=os.getenv("WA_THREAD_ID", "wa-thread-1001"),
    subject="בקשה להצעת מחיר",
    contact=Contact(full_name="דנה כהן", phone=os.getenv("CUSTOMER_PHONE", "050-123-4567"), company="כהן עיצוב"),
    messages=[ConversationMessage("wa-1001", "18/02/2026 09:44:00", "inbound", "אפשר לקבל הצעת מחיר עד ₪2,500?")],
    consent=ConsentRecord(marketing_opt_in=False, evidence="פנייה יזומה של לקוחה"),
    business_purpose="sales",
)
client = CRMIntegrationClient.from_env("monday", environment=args.env, dry_run=args.env == "sandbox", monday_board_id=os.getenv("MONDAY_BOARD_ID", "DRY_RUN_BOARD"))
result = client.sync_thread(thread)
print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
