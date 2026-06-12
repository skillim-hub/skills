#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from terminology_glossary_builder import GlossaryBuilder

DEFAULT_TERMS = ['Exempt dealer', 'Licensed dealer', 'Withholding tax', 'National Insurance contributions']


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a freelancer tax glossary.')
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TGB_ENV", "sandbox"))
    parser.add_argument("--output-dir", default=os.getenv("TGB_OUTPUT_DIR", ""))
    args = parser.parse_args()

    terms = [part.strip() for part in os.getenv("TGB_TERMS", ",".join(DEFAULT_TERMS)).split(",") if part.strip()]
    builder = GlossaryBuilder()
    result = builder.build_glossary(
        terms,
        industry='freelance',
        audience='freelancer',
        environment=args.env,
        title='Freelancer Tax Glossary',
    )
    payload = result.to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / 'freelancer-tax-glossary.md').write_text(builder.to_markdown(result, localization='en'), encoding="utf-8")


if __name__ == "__main__":
    main()
