from _example_common import client, env_value, parser, print_json

args = parser("Generate an accountant missing-documents reminder.").parse_args()
request = client.FollowupRequest(
    business_name=env_value("BUSINESS_NAME", "כהן הנהלת חשבונות", mode=args.env),
    customer_name=env_value("CUSTOMER_NAME", "יואב", mode=args.env),
    event_type=client.EventType.MISSING_DOCUMENTS,
    event_date=env_value("EVENT_DATE", "03/06/2026", mode=args.env),
    channel=env_value("CHANNEL", "whatsapp", mode=args.env),
    business_type="accountant",
    period_label=env_value("PERIOD_LABEL", "מאי 2026", mode=args.env),
    due_date=env_value("DUE_DATE", "10/06/2026", mode=args.env),
)
print_json(client.FollowupSolicitorClient().generate_plan(request))
