from _example_common import client, env_value, parser, print_json

args = parser("Generate a review request after positive customer feedback.").parse_args()
request = client.FollowupRequest(
    business_name=env_value("BUSINESS_NAME", "אור חשמל", mode=args.env),
    customer_name=env_value("CUSTOMER_NAME", "דנה", mode=args.env),
    event_type=client.EventType.REVIEW_REQUEST,
    event_date=env_value("EVENT_DATE", "03/06/2026", mode=args.env),
    channel=env_value("CHANNEL", "whatsapp", mode=args.env),
    sentiment=client.Sentiment.POSITIVE,
    review_url=env_value("REVIEW_URL", "https://g.page/r/example/review", mode=args.env),
)
print_json(client.FollowupSolicitorClient().generate_plan(request))
