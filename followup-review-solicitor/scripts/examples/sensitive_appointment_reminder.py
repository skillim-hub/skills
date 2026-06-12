from _example_common import client, env_value, parser, print_json

args = parser("Generate a sensitive appointment reminder.").parse_args()
request = client.FollowupRequest(
    business_name=env_value("BUSINESS_NAME", "קליניקה", mode=args.env),
    customer_name=env_value("CUSTOMER_NAME", "דנה", mode=args.env),
    event_type=client.EventType.APPOINTMENT_REMINDER,
    event_date=env_value("EVENT_DATE", "04/06/2026", mode=args.env),
    appointment_time=env_value("APPOINTMENT_TIME", "10:30", mode=args.env),
    channel=env_value("CHANNEL", "sms", mode=args.env),
    business_type="clinic",
)
print_json(client.FollowupSolicitorClient().generate_plan(request))
