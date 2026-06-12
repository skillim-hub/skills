#!/usr/bin/env python3
"""Hebrew-to-Latin transliteration helper for passport-aware Israeli names.

The module is intentionally local-only. It performs deterministic transliteration,
returns structured warnings for ambiguous Hebrew spelling, and supports synchronous
and asynchronous use.
"""

from __future__ import annotations

import asyncio
import csv
import json
import re
import unicodedata
from datetime import datetime, timezone
from uuid import uuid4
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence


OutputCase = Literal["upper", "title", "lower", "preserve"]
TzadiStyle = Literal["z", "tz", "ts"]

HEBREW_BLOCK_RE = re.compile(r"[\u0590-\u05FF]")
LATIN_RE = re.compile(r"[A-Za-z]")
NIQQUD_RE = re.compile(r"[\u0591-\u05BD\u05BF-\u05C7]")
HEBREW_LETTER_RE = re.compile(r"[\u05D0-\u05EA]")
SEPARATOR_RE = re.compile(r"(\s+|[-/])")

DAGESH = "\u05BC"
SHIN_DOT = "\u05C1"
SIN_DOT = "\u05C2"
HOLAM = "\u05B9"
QUBUTS = "\u05BB"
HIRIQ = "\u05B4"
TSERE = "\u05B5"
SEGOL = "\u05B6"
PATAH = "\u05B7"
QAMATS = "\u05B8"
SHEVA = "\u05B0"
HATAF_SEGOL = "\u05B1"
HATAF_PATAH = "\u05B2"
HATAF_QAMATS = "\u05B3"

FINAL_FORMS = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

LOAN_LETTERS = {
    "ג'": "J",
    "ג׳": "J",
    "ז'": "ZH",
    "ז׳": "ZH",
    "צ'": "CH",
    "צ׳": "CH",
    "ד'": "D",
    "ד׳": "D",
    "ת'": "TH",
    "ת׳": "TH",
}

# Common Israeli first names and surnames where unpointed Hebrew requires
# conventional vowels. Values are uppercase by design and transformed later.
KNOWN_NAMES: dict[str, str] = {
    "אביב": "AVIV",
    "אביגיל": "AVIGAIL",
    "אבי": "AVI",
    "אביעד": "AVIAD",
    "אברהם": "AVRAHAM",
    "אהרן": "AHARON",
    "אהרון": "AHARON",
    "אור": "OR",
    "אורי": "URI",
    "אורן": "OREN",
    "אייל": "EYAL",
    "איתן": "EITAN",
    "אילן": "ILAN",
    "אילנה": "ILANA",
    "אלון": "ALON",
    "אלי": "ELI",
    "אליהו": "ELIYAHU",
    "אליה": "ELIYA",
    "אליהב": "ELYAHAV",
    "אלירז": "ELIRAZ",
    "אלישבע": "ELISHEVA",
    "אסף": "ASAF",
    "אפרת": "EFRAT",
    "אריאל": "ARIEL",
    "אריאלה": "ARIELA",
    "אריה": "ARYE",
    "בועז": "BOAZ",
    "בר": "BAR",
    "ברק": "BARAK",
    "ברכה": "BRACHA",
    "גבריאל": "GABRIEL",
    "גדעון": "GIDEON",
    "גולן": "GOLAN",
    "גיא": "GUY",
    "גיל": "GIL",
    "גילה": "GILA",
    "גלעד": "GILAD",
    "דבורה": "DVORA",
    "דוד": "DAVID",
    "דויד": "DAVID",
    "דור": "DOR",
    "דורון": "DORON",
    "דינה": "DINA",
    "דנה": "DANA",
    "דניאל": "DANIEL",
    "דניאלה": "DANIELA",
    "הגר": "HAGAR",
    "הילה": "HILA",
    "הלל": "HILLEL",
    "זאב": "ZEEV",
    "חגי": "HAGAI",
    "חוה": "HAVA",
    "חיים": "HAIM",
    "חיה": "HAYA",
    "חנה": "HANA",
    "חן": "HEN",
    "טל": "TAL",
    "טלי": "TALI",
    "יובל": "YUVAL",
    "יואב": "YOAV",
    "יואל": "YOEL",
    "יונה": "YONA",
    "יונתן": "YONATAN",
    "יוסי": "YOSSI",
    "יוסף": "YOSEF",
    "יהודה": "YEHUDA",
    "יהודית": "YEHUDIT",
    "יעקב": "YAAKOV",
    "יעל": "YAEL",
    "יפה": "YAFA",
    "יצחק": "YIZHAK",
    "ישראל": "YISRAEL",
    "ישי": "YISHAI",
    "ישועה": "YESHUA",
    "כוכבה": "KOKHAVA",
    "כהן": "KOHEN",
    "כלפון": "KALFON",
    "כרמל": "KARMEL",
    "לאה": "LEA",
    "לביא": "LAVI",
    "לוי": "LEVI",
    "ליאור": "LIOR",
    "מאיר": "MEIR",
    "מור": "MOR",
    "מורן": "MORAN",
    "מיכאל": "MICHAEL",
    "מיכל": "MICHAL",
    "מירב": "MEIRAV",
    "מרים": "MIRIAM",
    "משה": "MOSHE",
    "מתן": "MATAN",
    "נבו": "NEVO",
    "נועה": "NOA",
    "נועם": "NOAM",
    "נורית": "NURIT",
    "נעמי": "NAOMI",
    "נתן": "NATAN",
    "נתנאל": "NETANEL",
    "עדי": "ADI",
    "עדן": "EDEN",
    "עומר": "OMER",
    "עמית": "AMIT",
    "ענבר": "INBAR",
    "פנינה": "PNINA",
    "פרץ": "PERETZ",
    "צבי": "ZVI",
    "קדם": "KEDEM",
    "רבקה": "RIVKA",
    "רון": "RON",
    "רוני": "RONI",
    "רות": "RUT",
    "רחל": "RAHEL",
    "שרה": "SARA",
    "שלום": "SHALOM",
    "שלמה": "SHLOMO",
    "שמעון": "SHIMON",
    "שמואל": "SHMUEL",
    "שירה": "SHIRA",
    "תמר": "TAMAR",
    "תומר": "TOMER",
    "בן": "BEN",
    "בת": "BAT",
    "בר-און": "BAR-ON",
    "בן-דוד": "BEN-DAVID",
    "כץ": "KATZ",
    "ג'ורג'": "GEORGE",
    "ג׳ורג׳": "GEORGE",
}

UNPOINTED_BASE = {
    "א": "",
    "ב": "B",
    "ג": "G",
    "ד": "D",
    "ה": "H",
    "ו": "V",
    "ז": "Z",
    "ח": "H",
    "ט": "T",
    "י": "Y",
    "כ": "KH",
    "ך": "KH",
    "ל": "L",
    "מ": "M",
    "ם": "M",
    "נ": "N",
    "ן": "N",
    "ס": "S",
    "ע": "",
    "פ": "F",
    "ף": "F",
    "צ": "Z",
    "ץ": "Z",
    "ק": "K",
    "ר": "R",
    "ש": "SH",
    "ת": "T",
}

POINTED_BASE = {
    "א": "",
    "ב": "V",
    "ג": "G",
    "ד": "D",
    "ה": "H",
    "ו": "V",
    "ז": "Z",
    "ח": "H",
    "ט": "T",
    "י": "Y",
    "כ": "KH",
    "ך": "KH",
    "ל": "L",
    "מ": "M",
    "ם": "M",
    "נ": "N",
    "ן": "N",
    "ס": "S",
    "ע": "",
    "פ": "F",
    "ף": "F",
    "צ": "Z",
    "ץ": "Z",
    "ק": "K",
    "ר": "R",
    "ש": "SH",
    "ת": "T",
}

VOWEL_MARKS = {
    HIRIQ: "I",
    TSERE: "E",
    SEGOL: "E",
    PATAH: "A",
    QAMATS: "A",
    HATAF_SEGOL: "E",
    HATAF_PATAH: "A",
    HATAF_QAMATS: "O",
    HOLAM: "O",
    QUBUTS: "U",
}


class TransliterationError(ValueError):
    """Base exception for transliteration errors."""


class TransliterationValidationError(TransliterationError):
    """Raised when input cannot be processed safely."""


@dataclass(frozen=True)
class TransliterationOptions:
    """Options controlling transliteration behavior."""

    output_case: OutputCase = "upper"
    use_known_names: bool = True
    strict: bool = False
    tzadi_style: TzadiStyle = "z"
    allow_mixed: bool = True
    explain: bool = False

    def normalized(self) -> "TransliterationOptions":
        if self.output_case not in {"upper", "title", "lower", "preserve"}:
            raise TransliterationValidationError(
                "output_case must be one of: upper, title, lower, preserve"
            )
        if self.tzadi_style not in {"z", "tz", "ts"}:
            raise TransliterationValidationError("tzadi_style must be one of: z, tz, ts")
        return self


@dataclass(frozen=True)
class TokenTrace:
    source: str
    output: str
    rule: str


@dataclass(frozen=True)
class TransliterationResult:
    original: str
    normalized: str
    latin: str
    warnings: tuple[str, ...] = field(default_factory=tuple)
    tokens: tuple[TokenTrace, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["warnings"] = list(self.warnings)
        data["tokens"] = [asdict(token) for token in self.tokens]
        return data

    def to_json(self, *, ensure_ascii: bool = False, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


def contains_hebrew(text: str) -> bool:
    return bool(HEBREW_BLOCK_RE.search(text))


def contains_latin(text: str) -> bool:
    return bool(LATIN_RE.search(text))


def strip_niqqud(text: str) -> str:
    return NIQQUD_RE.sub("", text)


def normalize_hebrew_text(text: str) -> str:
    value = unicodedata.normalize("NFC", text)
    value = value.replace("\u05BE", "-")  # maqaf
    value = value.replace("־", "-")
    value = value.replace("–", "-").replace("—", "-")
    value = value.replace("׳", "'").replace("״", '"')
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _plain_hebrew_key(word: str) -> str:
    return strip_niqqud(normalize_hebrew_text(word)).replace('"', "")


def _tzadi(options: TransliterationOptions) -> str:
    return {"z": "Z", "tz": "TZ", "ts": "TS"}[options.tzadi_style]


def _title_case(value: str) -> str:
    def cap(match: re.Match[str]) -> str:
        word = match.group(0)
        return word[:1].upper() + word[1:].lower()

    return re.sub(r"[A-Za-z]+", cap, value)


def apply_output_case(value: str, output_case: OutputCase) -> str:
    if output_case == "upper":
        return value.upper()
    if output_case == "lower":
        return value.lower()
    if output_case == "title":
        return _title_case(value)
    return value


def _split_clusters(word: str) -> list[tuple[str, str]]:
    clusters: list[tuple[str, str]] = []
    base = ""
    marks = ""
    for char in word:
        if HEBREW_LETTER_RE.match(char):
            if base:
                clusters.append((base, marks))
            base = char
            marks = ""
        else:
            marks += char
    if base:
        clusters.append((base, marks))
    return clusters


def _vowel_from_marks(marks: str, *, base: str) -> str:
    if DAGESH in marks and base == "ו" and not any(mark in marks for mark in VOWEL_MARKS):
        return "U"
    for mark in (HIRIQ, TSERE, SEGOL, PATAH, QAMATS, HATAF_SEGOL, HATAF_PATAH, HATAF_QAMATS, HOLAM, QUBUTS):
        if mark in marks:
            return VOWEL_MARKS[mark]
    return ""


def _transliterate_pointed_word(word: str, options: TransliterationOptions) -> tuple[str, list[str], list[TokenTrace]]:
    warnings: list[str] = []
    traces: list[TokenTrace] = []
    out: list[str] = []
    clusters = _split_clusters(word)
    for idx, (base, marks) in enumerate(clusters):
        if base in FINAL_FORMS:
            norm_base = base
        else:
            norm_base = base

        if base in {"צ", "ץ"}:
            consonant = _tzadi(options)
        elif base == "ב":
            consonant = "B" if DAGESH in marks else "V"
        elif base in {"כ", "ך"}:
            consonant = "K" if DAGESH in marks else "KH"
        elif base in {"פ", "ף"}:
            consonant = "P" if DAGESH in marks else "F"
        elif base == "ש":
            consonant = "S" if SIN_DOT in marks else "SH"
        elif base == "ו" and (
            (DAGESH in marks and not any(mark in marks for mark in VOWEL_MARKS))
            or HOLAM in marks
            or QUBUTS in marks
        ):
            consonant = ""
        else:
            consonant = POINTED_BASE.get(norm_base, "")

        vowel = _vowel_from_marks(marks, base=base)
        if base in {"א", "ע"}:
            segment = vowel
        elif base == "ה" and idx == len(clusters) - 1 and not vowel and len(clusters) > 1:
            segment = ""
        else:
            segment = consonant + vowel
        out.append(segment)
        traces.append(TokenTrace(base + marks, segment, "pointed-letter"))
    return "".join(out), warnings, traces


def _replace_loan_letters(word: str) -> tuple[str, list[TokenTrace]]:
    traces: list[TokenTrace] = []
    value = word
    for hebrew, latin in sorted(LOAN_LETTERS.items(), key=lambda item: len(item[0]), reverse=True):
        if hebrew in value:
            value = value.replace(hebrew, f"{{{latin}}}")
            traces.append(TokenTrace(hebrew, latin, "loan-letter-geresh"))
    return value, traces


def _transliterate_unpointed_word(word: str, options: TransliterationOptions) -> tuple[str, list[str], list[TokenTrace]]:
    warnings: list[str] = []
    traces: list[TokenTrace] = []

    key = _plain_hebrew_key(word)
    if options.use_known_names and not options.strict and key in KNOWN_NAMES:
        latin = KNOWN_NAMES[key]
        return latin, ("known-name-override",), [TokenTrace(word, latin, "known-name-override")]

    if any(char in key for char in "ואעיה") and not options.strict:
        warnings.append("unpointed_hebrew_ambiguous_vowels")
    if any(char in key for char in "בכפ"):
        warnings.append("unpointed_hebrew_dagesh_not_marked")

    prepared, loan_traces = _replace_loan_letters(word)
    traces.extend(loan_traces)

    out: list[str] = []
    letters = list(prepared)
    i = 0
    letter_index = 0
    hebrew_letters = [c for c in key if HEBREW_LETTER_RE.match(c)]
    while i < len(letters):
        char = letters[i]
        if char == "{":
            end = prepared.find("}", i)
            if end != -1:
                token = prepared[i + 1 : end]
                out.append(token)
                i = end + 1
                letter_index += 1
                continue

        if not HEBREW_LETTER_RE.match(char):
            i += 1
            continue

        is_first = letter_index == 0
        is_last = letter_index == len(hebrew_letters) - 1
        prev_letter = hebrew_letters[letter_index - 1] if letter_index else ""
        next_letter = hebrew_letters[letter_index + 1] if not is_last else ""

        if char in {"צ", "ץ"}:
            latin = _tzadi(options)
        elif char == "א":
            latin = "A" if is_first and not options.strict else ""
        elif char == "ע":
            latin = "A" if is_first and not options.strict else ""
        elif char == "ה" and is_last and len(hebrew_letters) > 1 and not options.strict:
            latin = "A"
        elif char == "י":
            if is_first:
                latin = "Y"
            elif is_last and not options.strict:
                latin = "I"
            elif next_letter and prev_letter and not options.strict:
                latin = "I"
            else:
                latin = "Y"
        elif char == "ו":
            if not options.strict and prev_letter and next_letter and prev_letter not in "אעוי" and next_letter not in "אעויה":
                latin = "O"
            else:
                latin = "V"
        elif char == "פ":
            latin = "P" if is_first and not options.strict else "F"
        elif char == "כ":
            latin = "K" if is_first and not options.strict else "KH"
        else:
            latin = UNPOINTED_BASE.get(char, "")
        out.append(latin)
        traces.append(TokenTrace(char, latin, "unpointed-letter"))
        i += 1
        letter_index += 1

    return "".join(out), warnings, traces


def _transliterate_hebrew_token(token: str, options: TransliterationOptions) -> tuple[str, list[str], list[TokenTrace]]:
    if NIQQUD_RE.search(token):
        return _transliterate_pointed_word(token, options)
    return _transliterate_unpointed_word(token, options)


def transliterate_hebrew_name(
    name: str,
    *,
    output_case: OutputCase = "upper",
    use_known_names: bool = True,
    strict: bool = False,
    tzadi_style: TzadiStyle = "z",
    allow_mixed: bool = True,
    explain: bool = False,
) -> TransliterationResult:
    """Transliterate a Hebrew personal or business-owner name to Latin script.

    Parameters mirror ``TransliterationOptions``. The result always contains a
    Latin value and may contain warnings when unpointed Hebrew prevents a single
    authoritative reading.
    """

    options = TransliterationOptions(
        output_case=output_case,
        use_known_names=use_known_names,
        strict=strict,
        tzadi_style=tzadi_style,
        allow_mixed=allow_mixed,
        explain=explain,
    ).normalized()

    if not isinstance(name, str):
        raise TransliterationValidationError("name must be a string")
    if not name.strip():
        raise TransliterationValidationError("name must not be empty")

    normalized = normalize_hebrew_text(name)
    has_hebrew = contains_hebrew(normalized)
    has_latin = contains_latin(normalized)
    warnings: list[str] = []
    traces: list[TokenTrace] = []

    if not has_hebrew:
        warnings.append("no_hebrew_detected")
        latin_only = apply_output_case(normalized, options.output_case)
        return TransliterationResult(name, normalized, latin_only, tuple(warnings), tuple())

    if has_latin:
        warnings.append("mixed_hebrew_latin_input")
        if not options.allow_mixed:
            raise TransliterationValidationError("mixed Hebrew/Latin input requires allow_mixed=True")

    parts = SEPARATOR_RE.split(normalized)
    output_parts: list[str] = []
    for part in parts:
        if part == "":
            continue
        if SEPARATOR_RE.fullmatch(part):
            output_parts.append(" " if part.isspace() else part)
            continue
        if contains_hebrew(part):
            latin, part_warnings, part_traces = _transliterate_hebrew_token(part, options)
            output_parts.append(latin)
            warnings.extend(part_warnings)
            traces.extend(part_traces)
        else:
            output_parts.append(part)
            traces.append(TokenTrace(part, part, "latin-or-neutral-preserved"))

    latin_value = "".join(output_parts)
    latin_value = re.sub(r"\s+", " ", latin_value).strip()
    latin_value = apply_output_case(latin_value, options.output_case)
    # Remove duplicate warnings while preserving order.
    warnings = list(dict.fromkeys(warnings))
    if not options.explain:
        traces = tuple()
    return TransliterationResult(name, normalized, latin_value, tuple(warnings), tuple(traces))


class TransliterationClient:
    """Typed local client for synchronous and asynchronous transliteration."""

    def __init__(self, default_options: TransliterationOptions | None = None) -> None:
        self.default_options = (default_options or TransliterationOptions()).normalized()

    def _merge_options(self, **overrides: Any) -> TransliterationOptions:
        data = {
            "output_case": self.default_options.output_case,
            "use_known_names": self.default_options.use_known_names,
            "strict": self.default_options.strict,
            "tzadi_style": self.default_options.tzadi_style,
            "allow_mixed": self.default_options.allow_mixed,
            "explain": self.default_options.explain,
        }
        data.update({k: v for k, v in overrides.items() if v is not None})
        return TransliterationOptions(**data).normalized()

    def transliterate(self, name: str, **overrides: Any) -> TransliterationResult:
        options = self._merge_options(**overrides)
        return transliterate_hebrew_name(
            name,
            output_case=options.output_case,
            use_known_names=options.use_known_names,
            strict=options.strict,
            tzadi_style=options.tzadi_style,
            allow_mixed=options.allow_mixed,
            explain=options.explain,
        )

    def transliterate_many(self, names: Sequence[str], **overrides: Any) -> list[TransliterationResult]:
        return [self.transliterate(name, **overrides) for name in names]

    async def transliterate_async(self, name: str, **overrides: Any) -> TransliterationResult:
        return await asyncio.to_thread(self.transliterate, name, **overrides)

    async def transliterate_many_async(self, names: Sequence[str], **overrides: Any) -> list[TransliterationResult]:
        tasks = [self.transliterate_async(name, **overrides) for name in names]
        return list(await asyncio.gather(*tasks))

    def transliterate_file(
        self,
        input_path: str | Path,
        *,
        output_path: str | Path | None = None,
        input_column: str | None = None,
        output_format: Literal["json", "csv", "text"] = "json",
        **overrides: Any,
    ) -> list[TransliterationResult]:
        path = Path(input_path)
        if not path.exists():
            raise TransliterationValidationError(f"input file does not exist: {path}")
        names: list[str] = []
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                column = input_column or "hebrew_name"
                if column not in (reader.fieldnames or []):
                    raise TransliterationValidationError(f"CSV column not found: {column}")
                names = [row[column] for row in reader if row.get(column)]
        else:
            names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

        results = self.transliterate_many(names, **overrides)
        if output_path is not None:
            write_results(results, output_path, output_format=output_format)
        return results

    def create_record(
        self,
        name: str,
        *,
        store_path: str | Path | None = None,
        **overrides: Any,
    ) -> dict[str, Any]:
        result = self.transliterate(name, **overrides)
        record = {
            "id": uuid4().hex,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "result": result.to_dict(),
        }
        if store_path is not None:
            append_record(record, store_path)
        return record

    def get_record(self, record_id: str, store_path: str | Path) -> dict[str, Any]:
        return read_record(record_id, store_path)


def append_record(record: dict[str, Any], store_path: str | Path) -> None:
    path = Path(store_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_record(record_id: str, store_path: str | Path) -> dict[str, Any]:
    path = Path(store_path)
    if not path.exists():
        raise TransliterationValidationError(f"store file does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("id") == record_id:
                return record
    raise TransliterationValidationError(f"record not found: {record_id}")


def write_results(
    results: Sequence[TransliterationResult],
    output_path: str | Path,
    *,
    output_format: Literal["json", "csv", "text"] = "json",
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        path.write_text(
            json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return
    if output_format == "csv":
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["original", "normalized", "latin", "warnings"])
            writer.writeheader()
            for result in results:
                writer.writerow(
                    {
                        "original": result.original,
                        "normalized": result.normalized,
                        "latin": result.latin,
                        "warnings": ";".join(result.warnings),
                    }
                )
        return
    if output_format == "text":
        path.write_text("\n".join(result.latin for result in results) + "\n", encoding="utf-8")
        return
    raise TransliterationValidationError("output_format must be one of: json, csv, text")


__all__ = [
    "KNOWN_NAMES",
    "TransliterationClient",
    "TransliterationError",
    "TransliterationOptions",
    "TransliterationResult",
    "TransliterationValidationError",
    "TokenTrace",
    "append_record",
    "apply_output_case",
    "contains_hebrew",
    "normalize_hebrew_text",
    "strip_niqqud",
    "transliterate_hebrew_name",
    "read_record",
    "write_results",
]
