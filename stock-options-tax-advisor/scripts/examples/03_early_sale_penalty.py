from _example_loader import env_float, parser, run_case

args = parser("Early sale before preferred-treatment date.").parse_args()
run_case(args.env, {
    "grant_type": "options",
    "track": "102_capital",
    "quantity": env_float("STOCK_OPTIONS_QUANTITY", 20000),
    "exercise_price": 2,
    "sale_price": env_float("STOCK_OPTIONS_SALE_PRICE", 14),
    "grant_date": "15/03/2024",
    "sale_date": "01/08/2025",
    "other_annual_income": env_float("STOCK_OPTIONS_OTHER_INCOME", 420000),
    "trustee_approved": True,
})
