# Reference: local interface, standards context, and error model

This skill has no remote API. It provides a local Python client and a local CLI for transliterating Hebrew names into Latin script using Israeli passport-aware conventions. Treat the output as a data-quality aid unless an official Latin spelling is unavailable and the workflow accepts generated spelling.

## Israeli regulatory and operational context

Use these reference points when deciding how much review is required:

| Area | Practical implication |
|---|---|
| Population and Immigration Authority / passport spelling practices | Travel-document spelling may follow several permitted bases. Preserve an existing passport spelling exactly. |
| Israeli identity and civil registry workflows | Hebrew civil names may not provide Latin spelling. Do not infer legal identity from transliteration alone. |
| Banking, insurance, travel, and payment-provider onboarding | Name mismatch can delay service. Prefer official Latin spelling over generated spelling. |
| Privacy and customer-data handling | Process names locally and avoid unnecessary disclosure to external tools. |
| Consumer and small-business recordkeeping | Keep source, generated value, warnings, review status, reviewer, and date. |

No government endpoint is called. No identity document is verified. No legal advice is provided. Confirm current official instructions before using automated output in a regulated submission.


## Web-validated official-source boundary

Current validation found no public government API, endpoint host, or webhook flow for this helper because the package is local-only. Treat the standards context as document guidance, not as a remote integration contract.

Travel-document Latin spelling is not one mandatory machine-generated value. Israeli travel-document rules permit the applicant's Latin spelling to be recorded by several bases, including simple Hebrew-to-Latin transliteration rules, established Latin spelling tradition, phonetic preservation, and accepted spelling in the applicant's country of birth or residence.

Use the Academy phrase `תעתיק מעברית לאותיות לטיניות` rather than `תעתיק מעברית לאנגלית`. For code and documentation, prefer `Latin script` over `English spelling` unless a specific English-language form is being discussed.

VAT is outside the transliteration engine. Examples that mention Israeli invoices or amounts should keep currency formatting such as `₪1,250` and avoid embedding tax-rate calculations unless a separate tax workflow verifies the current rate. The live validation log records the 18% VAT check requested for Israeli small-business context.

## Python client

### Import

Install the project, then import the module directly:

```bash
pip install -e .
```

```python
from transliteration_helper_client import TransliterationClient
```

### Sync request

```python
from transliteration_helper_client import TransliterationClient

client = TransliterationClient()
result = client.transliterate("דוד כהן")
print(result.latin)
```

Response:

```json
{
  "original": "דוד כהן",
  "normalized": "דוד כהן",
  "latin": "DAVID KOHEN",
  "warnings": [],
  "tokens": []
}
```

### Async request

```python
import asyncio
from transliteration_helper_client import TransliterationClient

async def run():
    client = TransliterationClient()
    return await client.transliterate_async("שרה לוי")

print(asyncio.run(run()).to_json())
```

### Batch request

```python
client = TransliterationClient()
results = client.transliterate_many(["דוד כהן", "שרה לוי", "בן־דוד"])
for item in results:
    print(item.latin, item.warnings)
```

### File request

Text file:

```text
דוד כהן
שרה לוי
בן־דוד
```

Python:

```python
client.transliterate_file("names.txt", output_path="out.csv", output_format="csv")
```

CSV file:

```csv
hebrew_name,customer_id
דוד כהן,1001
שרה לוי,1002
```

Python:

```python
client.transliterate_file(
    "customers.csv",
    input_column="hebrew_name",
    output_path="latin_names.json",
    output_format="json"
)
```

## Local record helpers

Use local records when a workflow needs a stable review identifier. The record store is a UTF-8 JSON Lines file.

```python
from transliteration_helper_client import TransliterationClient

client = TransliterationClient()
created = client.create_record("שרה לוי", store_path="./tmp/transliteration-records.jsonl")
record_id = created["id"]
loaded = client.get_record(record_id, "./tmp/transliteration-records.jsonl")
print(loaded["result"]["latin"])
```

Create response:

```json
{
  "id": "f0d8b6fbd0ce4e9f9c2f4ed1a4f74d7c",
  "created_at": "2026-06-03T07:00:00+00:00",
  "result": {
    "original": "שרה לוי",
    "normalized": "שרה לוי",
    "latin": "SARA LEVI",
    "warnings": [],
    "tokens": []
  }
}
```

## CLI reference

### Command: transliterate

```bash
python scripts/transliteration-helper-cli.py transliterate "דוד כהן"
```

Options:

| Option | Values | Default | Meaning |
|---|---|---:|---|
| `--format` | `text`, `json` | `text` | Output format |
| `--case` | `upper`, `title`, `lower`, `preserve` | `upper` | Letter case |
| `--strict` | flag | off | Disable common-name overrides |
| `--no-known` | flag | off | Disable common-name dictionary |
| `--tzadi-style` | `z`, `tz`, `ts` | `z` | Rendering for צ/ץ |
| `--allow-mixed/--reject-mixed` | boolean | allow | Mixed Hebrew/Latin input |
| `--explain` | flag | off | Include token rule traces in JSON |

### Command: create

```bash
python scripts/transliteration-helper-cli.py create --store ./tmp/transliteration-records.jsonl "שרה לוי"
```

Returns a JSON object with an `id`. Store the `id` in a review queue, customer-note table, or audit note.

### Command: show

```bash
python scripts/transliteration-helper-cli.py show --store ./tmp/transliteration-records.jsonl RECORD_ID
```

Reads one record from the local JSON Lines store.

JSON example:

```bash
python scripts/transliteration-helper-cli.py transliterate --format json --explain "ג׳ורג׳ כהן"
```

Response:

```json
{
  "original": "ג׳ורג׳ כהן",
  "normalized": "ג'ורג' כהן",
  "latin": "GEORGE KOHEN",
  "warnings": [],
  "tokens": [
    {
      "source": "ג'ורג'",
      "output": "GEORGE",
      "rule": "known-name-override"
    },
    {
      "source": "כהן",
      "output": "KOHEN",
      "rule": "known-name-override"
    }
  ]
}
```

### Command: batch

```bash
python scripts/transliteration-helper-cli.py batch -i customers.csv --input-column hebrew_name --format csv -o out.csv
```

CSV response columns:

| Column | Description |
|---|---|
| `original` | Original input string |
| `normalized` | Normalized Hebrew and punctuation |
| `latin` | Latin-script output |
| `warnings` | Semicolon-separated warning codes |

### Command: validate

```bash
python scripts/transliteration-helper-cli.py validate "אבתיה"
```

Use this before sending high-impact forms. It returns warnings and token traces.

## Data schemas

### TransliterationResult

```json
{
  "type": "object",
  "required": ["original", "normalized", "latin", "warnings", "tokens"],
  "properties": {
    "original": {"type": "string"},
    "normalized": {"type": "string"},
    "latin": {"type": "string"},
    "warnings": {"type": "array", "items": {"type": "string"}},
    "tokens": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["source", "output", "rule"],
        "properties": {
          "source": {"type": "string"},
          "output": {"type": "string"},
          "rule": {"type": "string"}
        }
      }
    }
  }
}
```

### Options schema

```json
{
  "output_case": "upper|title|lower|preserve",
  "use_known_names": true,
  "strict": false,
  "tzadi_style": "z|tz|ts",
  "allow_mixed": true,
  "explain": false
}
```

## Warning table

| Warning | Meaning | Recommended action |
|---|---|---|
| `no_hebrew_detected` | Input has no Hebrew characters | Preserve official Latin spelling or confirm source |
| `mixed_hebrew_latin_input` | Input contains both Hebrew and Latin | Check whether Latin part is official |
| `unpointed_hebrew_ambiguous_vowels` | Hebrew lacks niqqud and vowels cannot be fully inferred | Review manually for high-impact use |
| `unpointed_hebrew_dagesh_not_marked` | ב/כ/פ may change sound depending on dagesh | Use niqqud, official spelling, or manual review |
| `known-name-override` | Common-name dictionary supplied the spelling | Keep source note when used automatically |

## Error table

| Error | Trigger | Fix |
|---|---|---|
| `name must be a string` | Non-string input | Convert before calling |
| `name must not be empty` | Empty or whitespace-only input | Reject row or request a name |
| `output_case must be one of...` | Unsupported case option | Use `upper`, `title`, `lower`, or `preserve` |
| `tzadi_style must be one of...` | Unsupported צ style | Use `z`, `tz`, or `ts` |
| `mixed Hebrew/Latin input requires allow_mixed=True` | Mixed script rejected | Enable mixed input or clean the data |
| `input file does not exist` | Missing path | Check path and working directory |
| `CSV column not found` | Missing input column | Use `--input-column` or rename header |
| `output_format must be one of...` | Unsupported output format | Use `json`, `csv`, or `text` |

## Request/response examples

### Consumer onboarding

Request:

```bash
python scripts/transliteration-helper-cli.py transliterate --format json "נועה פרץ"
```

Response:

```json
{
  "latin": "NOA PERETZ",
  "warnings": []
}
```

### Invoice for a freelancer

Request:

```bash
python scripts/transliteration-helper-cli.py transliterate --case title "שרה לוי"
```

Response:

```text
Sara Levi
```

### Review queue

Request:

```bash
python scripts/transliteration-helper-cli.py validate "אבתיה"
```

Response:

```json
{
  "latin": "ABTIA",
  "warnings": [
    "unpointed_hebrew_ambiguous_vowels",
    "unpointed_hebrew_dagesh_not_marked"
  ]
}
```

### Alternate צ convention

Request:

```bash
python scripts/transliteration-helper-cli.py transliterate --strict --tzadi-style tz "צבי"
```

Response:

```text
TZVY
```

Use the alternate style only when the target system or customer record requires it.
