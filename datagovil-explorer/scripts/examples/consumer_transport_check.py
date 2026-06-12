from _example_common import client_from_args, parser, print_json

args_parser = parser("Find datasets for consumer checks about bus and train services.")
args_parser.add_argument("--query", default="תעריפי תחבורה ציבורית")
args_parser.add_argument("--rows", type=int, default=5)
args = args_parser.parse_args()
client = client_from_args(args)
print_json(client.package_search(args.query, rows=args.rows, sort="metadata_modified desc"))
