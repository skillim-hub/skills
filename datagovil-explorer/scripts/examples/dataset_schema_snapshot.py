from _example_common import client_from_args, parser, print_json
from datagovil_explorer import extract_first_resource_id

args_parser = parser("Show the first resource and field metadata for a dataset.")
args_parser.add_argument("dataset_id")
args = args_parser.parse_args()
client = client_from_args(args)
dataset = client.package_show(args.dataset_id)
resource_id = extract_first_resource_id(dataset, prefer_datastore=True)
resource = client.resource_show(resource_id) if resource_id else {}
print_json({"dataset": dataset.get("name"), "resource_id": resource_id, "fields": resource.get("fields", [])})
