from pathlib import Path

from _example_common import client_from_args, parser, print_json
from datagovil_explorer import DatagovClient, parse_filter_pairs

args_parser = parser("Export a datastore resource to CSV.")
args_parser.add_argument("resource_id")
args_parser.add_argument("--out", default="resource-export.csv")
args_parser.add_argument("--max-records", type=int, default=100)
args_parser.add_argument("--filter", action="append", default=[])
args = args_parser.parse_args()
client = client_from_args(args)
filters = parse_filter_pairs(args.filter)
records = list(client.datastore_search_all(args.resource_id, max_records=args.max_records, filters=filters or None))
count = DatagovClient.write_csv(records, Path(args.out))
print_json({"rows_written": count, "output": args.out})
