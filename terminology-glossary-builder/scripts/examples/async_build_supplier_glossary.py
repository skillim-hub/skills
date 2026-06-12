#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os

from terminology_glossary_builder import GlossaryBuilder


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Build a supplier glossary asynchronously.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TGB_ENV", "sandbox"))
    args = parser.parse_args()
    terms = [part.strip() for part in os.getenv("TGB_TERMS", "Tax invoice,Receipt,Withholding tax").split(",") if part.strip()]
    result = await GlossaryBuilder().abuild_glossary(
        terms,
        industry="accounting",
        audience="small_business",
        environment=args.env,
        title="Supplier Accounting Glossary",
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
