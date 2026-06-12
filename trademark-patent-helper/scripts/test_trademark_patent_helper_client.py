from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from trademark_patent_helper import (
    FilingHelperClient,
    dedupe,
    flatten_text,
    normalize_il_date,
    tokenize,
)


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "scripts" / "trademark-patent-helper-cli.py"

CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


def run_cli(args, **kwargs):
    return subprocess.run([sys.executable, str(CLI_PATH), *args], env=CLI_ENV, capture_output=True, text=True, check=True, **kwargs)


def assess(payload):
    return FilingHelperClient().assess(payload)


def test_missing_kind_returns_unknown():
    result = assess({})
    assert result.kind == "unknown"
    assert "MISSING_KIND" in result.issue_codes


def test_unknown_kind():
    result = assess({"kind": "design"})
    assert result.kind == "unknown"
    assert "UNKNOWN_KIND" in result.issue_codes


def test_classify_trademark_from_brand_text():
    kind = FilingHelperClient().classify_asset({"description": "brand sign for a cafe"})
    assert kind == "trademark"


def test_classify_patent_from_invention_text():
    kind = FilingHelperClient().classify_asset({"description": "technical invention with a sensor"})
    assert kind == "patent"


def test_environment_validation():
    with pytest.raises(ValueError):
        FilingHelperClient(environment="staging")


def test_invented_mark_green():
    result = assess({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    })
    assert result.risk_level == "green"


def test_descriptive_mark_red():
    result = assess({
        "kind": "trademark",
        "mark_text": "FAST TAX REFUNDS",
        "classes": [{"class_no": 35, "items": ["tax refund assistance"]}],
    })
    assert result.risk_level == "red"
    assert "DESCRIPTIVE_MARK" in result.issue_codes


def test_hebrew_descriptive_mark():
    result = assess({
        "kind": "trademark",
        "mark_text": "החזרי מס מהירים",
        "classes": [{"class_no": 35, "items": ["סיוע בהחזרי מס"]}],
    })
    assert "DESCRIPTIVE_MARK" in result.issue_codes


def test_invalid_class():
    result = assess({
        "kind": "trademark",
        "mark_text": "NOVA",
        "classes": [{"class_no": 99, "items": ["software"]}],
    })
    assert "INVALID_CLASS" in result.issue_codes


def test_missing_mark():
    result = assess({"kind": "trademark", "classes": [{"class_no": 25, "items": ["shirts"]}]})
    assert "MISSING_MARK" in result.issue_codes


def test_missing_classes():
    result = assess({"kind": "trademark", "mark_text": "FLOWKITE"})
    assert "MISSING_CLASSES" in result.issue_codes


def test_broad_classes_warning():
    result = assess({
        "kind": "trademark",
        "mark_text": "FLOWKITE",
        "classes": [{"class_no": n, "items": ["sample"]} for n in range(1, 7)],
    })
    assert "BROAD_CLASSES" in result.issue_codes


def test_saas_class_step():
    result = assess({
        "kind": "trademark",
        "mark_text": "FLOWDESK",
        "classes": [{"class_no": 42, "items": ["software as a service"]}],
    })
    assert any("SaaS" in step for step in result.next_steps)


def test_class_35_step():
    result = assess({
        "kind": "trademark",
        "mark_text": "CRAFTNEST",
        "classes": [{"class_no": 35, "items": ["online marketplace services"]}],
    })
    assert any("Class 35" in step for step in result.next_steps)


def test_regulated_trademark():
    result = assess({
        "kind": "trademark",
        "mark_text": "MEDNOVA",
        "classes": [{"class_no": 44, "items": ["medical clinic services"]}],
    })
    assert "REGULATED_FIELD" in result.issue_codes


def test_patent_missing_title():
    result = assess({"kind": "patent", "solution": "A controller adjusts a valve using pressure sensor data.", "novel_features": ["threshold table"]})
    assert "MISSING_TITLE" in result.issue_codes


def test_patent_missing_technical_detail():
    result = assess({"kind": "patent", "title": "Smart watering", "solution": "An app.", "novel_features": ["unknown"]})
    assert "MISSING_TECHNICAL_DETAIL" in result.issue_codes


def test_patent_no_novel_features():
    result = assess({"kind": "patent", "title": "Valve", "solution": "A controller adjusts a valve using pressure sensor data and downstream thresholds."})
    assert "NO_NOVEL_FEATURES" in result.issue_codes


def test_patent_public_disclosure_red():
    result = assess({
        "kind": "patent",
        "title": "Bike lock",
        "solution": "A lock includes a rotating cam, spring latch, and keyed controller module.",
        "novel_features": ["spring latch geometry"],
        "public_disclosures": [{"date": "12/04/2026", "channel": "YouTube"}],
    })
    assert result.risk_level == "red"
    assert "PUBLIC_DISCLOSURE" in result.issue_codes


def test_patent_ownership_risk():
    result = assess({
        "kind": "patent",
        "title": "Sensor device",
        "solution": "A sensor device includes a processor, memory, and calibration circuit.",
        "novel_features": ["calibration circuit"],
        "ownership": "made by employee during work",
    })
    assert "OWNERSHIP_RISK" in result.issue_codes


def test_patent_business_method_risk():
    result = assess({
        "kind": "patent",
        "title": "Gym pricing",
        "solution": "A subscription pricing model for gyms with discounts.",
        "novel_features": ["pricing tiers"],
    })
    assert "BUSINESS_METHOD_RISK" in result.issue_codes


def test_async_assessment():
    result = asyncio.run(FilingHelperClient().assess_async({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    }))
    assert result.kind == "trademark"


def test_create_and_get_roundtrip(tmp_path):
    state = tmp_path / "records.json"
    helper = FilingHelperClient(environment="sandbox")
    created = helper.create({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    }, state_path=state)
    fetched = helper.get(created.request_id, state_path=state)
    assert fetched.request_id == created.request_id
    assert fetched.kind == "trademark"


def test_get_missing_record(tmp_path):
    result = FilingHelperClient().get("missing", state_path=tmp_path / "records.json")
    assert "NOT_FOUND" in result.issue_codes


def test_markdown_contains_risk():
    result = assess({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    })
    md = result.to_markdown()
    assert "Risk level" in md
    assert "trademark" in md.lower()


def test_json_roundtrip():
    result = assess({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    })
    data = json.loads(result.to_json())
    assert data["kind"] == "trademark"


def test_normalize_iso_date():
    assert normalize_il_date("2026-05-03") == "03/05/2026"


def test_normalize_slash_date():
    assert normalize_il_date("03/05/2026") == "03/05/2026"


def test_normalize_hyphen_date():
    assert normalize_il_date("03-05-2026") == "03/05/2026"


def test_normalize_bad_date():
    with pytest.raises(ValueError):
        normalize_il_date("May 3")


def test_dedupe():
    assert dedupe(["a", "a", "b"]) == ["a", "b"]


def test_tokenize_hebrew_and_english():
    tokens = tokenize("NOVA נובה 123")
    assert "nova" in tokens
    assert "נובה" in tokens


def test_flatten_text_nested():
    text = flatten_text({"a": ["medical", {"b": "device"}]})
    assert "medical" in text and "device" in text


def test_cli_template_trademark():
    proc = run_cli(["template", "trademark"])
    assert '"kind": "trademark"' in proc.stdout


def test_cli_assess_json(tmp_path):
    payload = tmp_path / "tm.json"
    payload.write_text(json.dumps({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    }), encoding="utf-8")
    proc = run_cli(["assess", str(payload), "--format", "json"])
    data = json.loads(proc.stdout)
    assert data["risk_level"] == "green"


def test_cli_assess_markdown(tmp_path):
    payload = tmp_path / "pat.json"
    payload.write_text(json.dumps({
        "kind": "patent",
        "title": "Valve",
        "solution": "A controller adjusts a valve using pressure sensor data and downstream thresholds.",
        "novel_features": ["downstream threshold control"],
    }), encoding="utf-8")
    proc = run_cli(["assess", str(payload), "--format", "markdown"])
    assert "Patent assessment" in proc.stdout


def test_cli_create_show_chain(tmp_path):
    payload = tmp_path / "tm.json"
    state = tmp_path / "records.json"
    payload.write_text(json.dumps({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    }), encoding="utf-8")
    created = run_cli(["create", str(payload), "--format", "json", "--state", str(state)])
    request_id = json.loads(created.stdout)["request_id"]
    shown = run_cli(["show", request_id, "--format", "json", "--state", str(state)])
    assert json.loads(shown.stdout)["request_id"] == request_id


def test_cli_intake():
    proc = run_cli(["intake", "technical", "invention", "with", "sensor", "--format", "json"])
    data = json.loads(proc.stdout)
    assert data["kind"] == "patent"


def test_cli_batch(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    }), encoding="utf-8")
    proc = run_cli(["batch", str(tmp_path), "--format", "json"])
    data = json.loads(proc.stdout)
    assert data[0]["file"] == "a.json"


def test_importable_package():
    helper = FilingHelperClient()
    result = helper.assess({
        "kind": "trademark",
        "mark_text": "ZAVILO",
        "classes": [{"class_no": 25, "items": ["clothing"]}],
    })
    assert result.risk_level == "green"
