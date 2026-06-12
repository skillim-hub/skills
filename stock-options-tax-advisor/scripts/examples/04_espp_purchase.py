from _example_loader import env_float, parser, run_case

args = parser("ESPP purchase discount and later appreciation split.").parse_args()
run_case(args.env, {
    "grant_type": "espp",
    "track": "3i",
    "quantity": env_float("STOCK_OPTIONS_QUANTITY", 300),
    "exercise_price": env_float("STOCK_OPTIONS_EXERCISE_PRICE", 80),
    "fmv_at_purchase": env_float("STOCK_OPTIONS_FMV_AT_PURCHASE", 100),
    "sale_price": env_float("STOCK_OPTIONS_SALE_PRICE", 120),
    "grant_date": "01/01/2025",
    "sale_date": "01/07/2025",
})
