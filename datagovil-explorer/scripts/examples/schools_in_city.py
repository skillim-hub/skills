from _example_common import client_from_args, parser, print_json

args_parser = parser("Search education datasets for a city term.")
args_parser.add_argument("--city", default="חיפה")
args_parser.add_argument("--rows", type=int, default=10)
args = args_parser.parse_args()
client = client_from_args(args)
print_json(client.package_search(f"בתי ספר {args.city}", rows=args.rows))
