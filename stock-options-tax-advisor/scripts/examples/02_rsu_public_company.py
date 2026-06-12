from _example_loader import env_float, parser, run_case

args = parser("Public-company RSU with grant-date FMV split.").parse_args()
run_case(args.env, {
    "grant_type": "rsu",
    "track": "102_capital",
    "quantity": env_float("STOCK_OPTIONS_QUANTITY", 1000),
    "exercise_price": 0,
    "sale_price": env_float("STOCK_OPTIONS_SALE_PRICE", 65),
    "fmv_at_grant": env_float("STOCK_OPTIONS_FMV_AT_GRANT", 40),
    "grant_date": "01/02/2024",
    "sale_date": "01/03/2027",
    "public_at_grant": True,
    "trustee_approved": True,
})
