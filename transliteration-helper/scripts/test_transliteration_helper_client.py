from __future__ import annotations

import asyncio
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
CLI_PATH = SCRIPT_DIR / "transliteration-helper-cli.py"

from transliteration_helper_client import (
    TransliterationClient,
    TransliterationValidationError,
    normalize_hebrew_text,
    strip_niqqud,
    transliterate_hebrew_name,
    write_results,
)



def run_async(coro):
    """Run a coroutine from regular pytest, including notebook-like runners."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import threading

    box = {}
    def target():
        try:
            box["value"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover
            box["error"] = exc

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box["value"]


def test_known_first_name_david():
    assert transliterate_hebrew_name("דוד").latin == "DAVID"


def test_known_full_name_with_space():
    assert transliterate_hebrew_name("דוד כהן").latin == "DAVID KOHEN"


def test_known_hyphenated_name():
    assert transliterate_hebrew_name("בן-דוד").latin == "BEN-DAVID"


def test_maqaf_normalizes_to_hyphen():
    result = transliterate_hebrew_name("בן־דוד")
    assert result.normalized == "בן-דוד"
    assert result.latin == "BEN-DAVID"


def test_title_case_output():
    assert transliterate_hebrew_name("דוד כהן", output_case="title").latin == "David Kohen"


def test_lower_case_output():
    assert transliterate_hebrew_name("דוד", output_case="lower").latin == "david"


def test_latin_only_preserved_with_warning():
    result = transliterate_hebrew_name("David Cohen")
    assert result.latin == "DAVID COHEN"
    assert "no_hebrew_detected" in result.warnings


def test_mixed_input_allowed_by_default():
    result = transliterate_hebrew_name("דוד Cohen")
    assert result.latin == "DAVID COHEN"
    assert "mixed_hebrew_latin_input" in result.warnings


def test_mixed_input_can_be_rejected():
    with pytest.raises(TransliterationValidationError):
        transliterate_hebrew_name("דוד Cohen", allow_mixed=False)


def test_empty_input_rejected():
    with pytest.raises(TransliterationValidationError):
        transliterate_hebrew_name("   ")


def test_invalid_case_rejected():
    with pytest.raises(TransliterationValidationError):
        transliterate_hebrew_name("דוד", output_case="sentence")  # type: ignore[arg-type]


def test_tzadi_default_z():
    assert transliterate_hebrew_name("צבי").latin == "ZVI"


def test_tzadi_style_tz_strict():
    assert transliterate_hebrew_name("צבי", strict=True, tzadi_style="tz").latin.startswith("TZ")


def test_pointed_bet_without_dagesh_is_v():
    assert transliterate_hebrew_name("בָּרָק").latin == "BARAK"
    assert transliterate_hebrew_name("בָרָק", use_known_names=False).latin == "VARAK"


def test_pointed_shin_and_sin():
    assert transliterate_hebrew_name("שָׁלוֹם", use_known_names=False).latin == "SHALOM"
    assert transliterate_hebrew_name("שָׂרָה", use_known_names=False).latin == "SARA"


def test_shuruk_vav():
    assert transliterate_hebrew_name("רוּת", use_known_names=False).latin == "RUT"


def test_niqqud_strip_helper():
    assert strip_niqqud("דָּוִד") == "דוד"


def test_normalize_apostrophes():
    assert normalize_hebrew_text("ג׳ורג׳") == "ג'ורג'"


def test_loan_letters_george():
    assert transliterate_hebrew_name("ג׳ורג׳").latin == "GEORGE"


def test_explain_includes_tokens():
    result = transliterate_hebrew_name("דוד", explain=True)
    assert result.tokens
    assert result.tokens[0].rule == "known-name-override"


def test_unpointed_unknown_warns_about_vowels():
    result = transliterate_hebrew_name("אבתיה", use_known_names=False)
    assert "unpointed_hebrew_ambiguous_vowels" in result.warnings


def test_client_many():
    client = TransliterationClient()
    assert [r.latin for r in client.transliterate_many(["דוד", "שרה"])] == ["DAVID", "SARA"]


def test_client_async_single():
    client = TransliterationClient()
    result = run_async(client.transliterate_async("משה"))
    assert result.latin == "MOSHE"


def test_client_async_many():
    client = TransliterationClient()
    results = run_async(client.transliterate_many_async(["דוד", "כהן", "לוי"]))
    assert [r.latin for r in results] == ["DAVID", "KOHEN", "LEVI"]


def test_to_json_round_trip():
    result = transliterate_hebrew_name("דוד", explain=True)
    payload = json.loads(result.to_json())
    assert payload["latin"] == "DAVID"


def test_write_results_json(tmp_path: Path):
    out = tmp_path / "out.json"
    write_results([transliterate_hebrew_name("דוד")], out, output_format="json")
    assert json.loads(out.read_text(encoding="utf-8"))[0]["latin"] == "DAVID"


def test_write_results_csv(tmp_path: Path):
    out = tmp_path / "out.csv"
    write_results([transliterate_hebrew_name("דוד")], out, output_format="csv")
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert rows[0]["latin"] == "DAVID"


def test_transliterate_file_text(tmp_path: Path):
    input_file = tmp_path / "names.txt"
    input_file.write_text("דוד\nשרה\n", encoding="utf-8")
    client = TransliterationClient()
    results = client.transliterate_file(input_file)
    assert [r.latin for r in results] == ["DAVID", "SARA"]


def test_transliterate_file_csv(tmp_path: Path):
    input_file = tmp_path / "names.csv"
    input_file.write_text("hebrew_name\nדוד\nשרה\n", encoding="utf-8")
    client = TransliterationClient()
    results = client.transliterate_file(input_file, input_column="hebrew_name")
    assert [r.latin for r in results] == ["DAVID", "SARA"]


def test_transliterate_file_missing_column(tmp_path: Path):
    input_file = tmp_path / "names.csv"
    input_file.write_text("name\nדוד\n", encoding="utf-8")
    client = TransliterationClient()
    with pytest.raises(TransliterationValidationError):
        client.transliterate_file(input_file, input_column="hebrew_name")


def test_cli_transliterate_text():
    proc = subprocess.run(
        [sys.executable, str(CLI_PATH), "transliterate", "דוד"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert proc.stdout.strip() == "DAVID"


def test_cli_json_output():
    proc = subprocess.run(
        [sys.executable, str(CLI_PATH), "transliterate", "--format", "json", "דוד"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert json.loads(proc.stdout)["latin"] == "DAVID"


def test_cli_batch_text(tmp_path: Path):
    input_file = tmp_path / "names.txt"
    input_file.write_text("דוד\nשרה\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(CLI_PATH), "batch", "-i", str(input_file), "--format", "text"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert proc.stdout.strip().splitlines() == ["DAVID", "SARA"]


def test_cli_validate_contains_warnings():
    proc = subprocess.run(
        [sys.executable, str(CLI_PATH), "validate", "אבתיה"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert "unpointed_hebrew_ambiguous_vowels" in payload["warnings"]

def test_client_create_and_get_record(tmp_path: Path):
    store = tmp_path / "records.jsonl"
    client = TransliterationClient()
    created = client.create_record("דוד כהן", store_path=store)
    loaded = client.get_record(created["id"], store)
    assert loaded["id"] == created["id"]
    assert loaded["result"]["latin"] == "DAVID KOHEN"


def test_cli_create_then_show_record(tmp_path: Path):
    store = tmp_path / "records.jsonl"
    create_proc = subprocess.run(
        [sys.executable, str(CLI_PATH), "create", "--store", str(store), "דוד כהן"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    created = json.loads(create_proc.stdout)
    show_proc = subprocess.run(
        [sys.executable, str(CLI_PATH), "show", "--store", str(store), created["id"]],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    shown = json.loads(show_proc.stdout)
    assert shown["id"] == created["id"]
    assert shown["result"]["latin"] == "DAVID KOHEN"
