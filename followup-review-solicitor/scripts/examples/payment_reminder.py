from _example_common import client, env_value, parser, print_json

args = parser("Generate a payment reminder.").parse_args()
request = client.FollowupRequest(
    business_name=env_value("BUSINESS_NAME", "סטודיו הבית", mode=args.env),
    customer_name=env_value("CUSTOMER_NAME", "נועה", mode=args.env),
    event_type=client.EventType.INVOICE_DUE,
    event_date=env_value("EVENT_DATE", "03/06/2026", mode=args.env),
    channel=env_value("CHANNEL", "email", mode=args.env),
    amount_ils=float(env_value("AMOUNT_ILS", "1250", mode=args.env)),
    payment_url=env_value("PAYMENT_URL", "https://pay.example.co.il/inv/1001", mode=args.env),
)
print_json(client.FollowupSolicitorClient().generate_plan(request))
