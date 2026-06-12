from _example_common import client, env_value, parser, print_json

args = parser("Generate a service completion check-in.").parse_args()
request = client.FollowupRequest(
    business_name=env_value("BUSINESS_NAME", "אור חשמל", mode=args.env),
    customer_name=env_value("CUSTOMER_NAME", "דנה", mode=args.env),
    event_type=client.EventType.SERVICE_COMPLETED,
    event_date=env_value("EVENT_DATE", "03/06/2026", mode=args.env),
    channel=env_value("CHANNEL", "whatsapp", mode=args.env),
    sentiment=client.Sentiment.UNKNOWN,
)
print_json(client.FollowupSolicitorClient().generate_plan(request))
