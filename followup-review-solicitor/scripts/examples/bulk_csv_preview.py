import csv
from io import StringIO

from _example_common import client, env_value, parser, print_json

args = parser("Generate a bulk CSV preview.").parse_args()
csv_text = env_value(
    "CSV_TEXT",
    """customer_name,phone,event_type,event_date,channel,sentiment,consent_status
דנה,050-123-4567,service_completed,03/06/2026,whatsapp,unknown,transactional
יואב,052-111-2222,missing_documents,03/06/2026,sms,unknown,transactional
""",
    mode=args.env,
)

rows = list(csv.DictReader(StringIO(csv_text)))
requests = [
    client.FollowupRequest(
        business_name=env_value("BUSINESS_NAME", "אור חשמל", mode=args.env),
        customer_name=row["customer_name"],
        phone=row["phone"],
        event_type=row["event_type"],
        event_date=row["event_date"],
        channel=row["channel"],
        sentiment=row["sentiment"],
        consent_status=row["consent_status"],
        period_label="מאי 2026" if row["event_type"] == "missing_documents" else None,
        due_date="10/06/2026" if row["event_type"] == "missing_documents" else None,
    )
    for row in rows
]
plans = client.FollowupSolicitorClient().generate_many(requests)
print_json([plan.to_dict() for plan in plans])
