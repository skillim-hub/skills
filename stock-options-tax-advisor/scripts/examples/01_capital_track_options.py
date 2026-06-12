from _example_loader import env_float, parser, run_case

args = parser("Section 102 capital track option sale after the trustee holding period.").parse_args()
run_case(args.env, {
    "grant_type": "options",
    "track": "102_capital",
    "quantity": env_float("STOCK_OPTIONS_QUANTITY", 50000),
    "exercise_price": env_float("STOCK_OPTIONS_EXERCISE_PRICE", 1),
    "sale_price": env_float("STOCK_OPTIONS_SALE_PRICE", 10),
    "grant_date": "15/03/2024",
    "sale_date": "02/01/2027",
    "other_annual_income": env_float("STOCK_OPTIONS_OTHER_INCOME", 360000),
    "trustee_approved": True,
})
