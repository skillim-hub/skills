from _example_common import client_from_args, parser, print_json

args_parser = parser("Search public transport datasets.")
args_parser.add_argument("--query", default="תחבורה ציבורית")
args_parser.add_argument("--rows", type=int, default=5)
args = args_parser.parse_args()
client = client_from_args(args)
print_json(client.package_search(args.query, rows=args.rows))
