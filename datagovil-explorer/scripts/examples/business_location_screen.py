from _example_common import client_from_args, parser, print_json

args_parser = parser("Screen datasets relevant to business location checks.")
args_parser.add_argument("--city", default="תל אביב")
args_parser.add_argument("--rows", type=int, default=8)
args = args_parser.parse_args()
client = client_from_args(args)
queries = ["רישוי עסקים", f"ארנונה {args.city}", f"תחבורה ציבורית {args.city}"]
print_json({query: client.package_search(query, rows=args.rows) for query in queries})
