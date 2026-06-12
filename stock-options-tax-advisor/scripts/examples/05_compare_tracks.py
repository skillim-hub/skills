import json

from _example_loader import env_float, parser
from stock_options_tax_advisor import EquityScenario, StockOptionsTaxAdvisorClient

args = parser("Compare common Israeli tax tracks.").parse_args()
client = StockOptionsTaxAdvisorClient(environment=args.env)
scenario = EquityScenario.from_dict({
    "grant_type": "options",
    "track": "102_capital",
    "quantity": env_float("STOCK_OPTIONS_QUANTITY", 10000),
    "exercise_price": env_float("STOCK_OPTIONS_EXERCISE_PRICE", 5),
    "sale_price": env_float("STOCK_OPTIONS_SALE_PRICE", 30),
    "fmv_at_exercise": env_float("STOCK_OPTIONS_FMV_AT_EXERCISE", 18),
    "grant_date": "01/04/2024",
    "sale_date": "02/01/2027",
    "other_annual_income": env_float("STOCK_OPTIONS_OTHER_INCOME", 250000),
    "trustee_approved": True,
})
print(json.dumps({"environment": client.environment, "results": {k: v.to_dict() for k, v in client.compare_tracks(scenario).items()}}, ensure_ascii=False, indent=2))
