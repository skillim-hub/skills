from __future__ import annotations

import argparse
import json
import os

from renovation_cost_estimator import RenovationCostEstimatorClient


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y"}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RENOVATION_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    project = {'project_name': 'שיפוץ קליניקה', 'city': 'תל אביב', 'property_type': 'clinic', 'area_sqm': 38, 'scope_level': 'commercial_fitout', 'finish_level': 'standard', 'include_vat': False, 'language': 'he'}
    project.setdefault("city", os.getenv("RENOVATION_CITY", project.get("city", "")))
    project.setdefault("property_type", os.getenv("RENOVATION_PROPERTY_TYPE", project.get("property_type", "apartment")))
    project.setdefault("scope_level", os.getenv("RENOVATION_SCOPE_LEVEL", project.get("scope_level", "partial")))
    project.setdefault("finish_level", os.getenv("RENOVATION_FINISH_LEVEL", project.get("finish_level", "standard")))
    if os.getenv("RENOVATION_AREA_SQM"):
        project["area_sqm"] = float(os.environ["RENOVATION_AREA_SQM"])
    if os.getenv("RENOVATION_INCLUDE_VAT"):
        project["include_vat"] = env_bool("RENOVATION_INCLUDE_VAT", bool(project.get("include_vat", True)))
    if os.getenv("RENOVATION_VAT_RATE"):
        project["vat_rate"] = float(os.environ["RENOVATION_VAT_RATE"])

    client = RenovationCostEstimatorClient()
    record = client.create_project(project, environment=args.env)
    result = client.estimate_by_id(record.id, environment=args.env)
    print(json.dumps({"create": {"id": record.id, "environment": record.environment}, "estimate": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
