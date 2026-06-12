from __future__ import annotations

import argparse
import json
import os
from typing import Any

from real_estate_search import Listing, RealEstateSearchClient, SearchCriteria


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("REAL_ESTATE_SEARCH_ENV", "sandbox"))
    return p


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
