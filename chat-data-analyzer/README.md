# Chat Data Analyzer

Analyze Hebrew and mixed Hebrew-English customer chats for small-business operations, support quality, privacy risk, and trend reporting.

The package includes:

- English and Hebrew skill guides.
- Israeli workflow and reference material.
- A typed synchronous and asynchronous Python client.
- A Click-based CLI.
- Pytest coverage with more than 20 tests.
- Runnable examples.

## What it does

- Detect Hebrew, English, and mixed-language messages.
- Classify common customer intents:
  - invoices, receipts, VAT, billing
  - appointments
  - deliveries
  - cancellations and refunds
  - product information
  - complaints
  - technical support
  - sales leads
  - privacy/legal terms
  - human-agent requests
- Score sentiment with transparent Hebrew-aware heuristics.
- Flag possible sensitive data:
  - email
  - Israeli mobile phone
  - valid Israeli ID-like value
  - Luhn-valid card-like value
  - URL
- Calculate first response time and average response time when timestamps exist.
- Mark drop-offs, escalation requests, and unresolved conversations.
- Export JSON and CSV summaries.

## Install

Requires Python 3.10 or newer.

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Quick start

Create a normalized conversation, extract the returned identifier, and use it in the next analysis call:

```python
from chat_data_analyzer_client import ChatDataAnalyzerClient

analyzer = ChatDataAnalyzerClient()
create_response = analyzer.create_conversation([
    {"sender": "user", "text": "אפשר לקבל חשבונית מס על 350 ₪?", "timestamp": "03/06/2026 09:00"},
    {"sender": "bot", "text": "כן. נא לשלוח מספר עוסק.", "timestamp": "03/06/2026 09:00"},
])

session_id = create_response["session_id"]
analysis = analyzer.analyze_conversation(create_response["messages"], session_id=session_id)
print(session_id)
print(analysis.primary_intent)
```

Create a sample file from the CLI:

```bash
chat-data-analyzer sample /tmp/chats.json
```

Analyze it:

```bash
chat-data-analyzer analyze /tmp/chats.json --format summary
```

Write JSON output:

```bash
chat-data-analyzer analyze /tmp/chats.json --format json -o /tmp/analysis.json
```

Write CSV output:

```bash
chat-data-analyzer analyze /tmp/chats.json --format csv -o /tmp/analysis.csv
```

Mask identifiers:

```bash
chat-data-analyzer anonymize /tmp/chats.json /tmp/chats.masked.json
```

Analyze one text snippet:

```bash
chat-data-analyzer text "המשלוח לא הגיע ואני רוצה החזר דחוף"
```

## Python usage

```python
from chat_data_analyzer_client import ChatDataAnalyzerClient

analyzer = ChatDataAnalyzerClient()
result = analyzer.analyze_text("אפשר לקבל חשבונית מס על 350 ₪?")
print(result["language"])
print(result["intents"][0]["intent"])
```

Async usage:

```python
import asyncio
from chat_data_analyzer_client import AsyncChatDataAnalyzerClient

async def main():
    analyzer = AsyncChatDataAnalyzerClient()
    result = await analyzer.analyze_text("לא מצליח להתחבר לאפליקציה")
    print(result["sentiment"])

asyncio.run(main())
```

## Input formats

### JSON

```json
[
  {
    "session_id": "s1",
    "messages": [
      {
        "sender": "user",
        "text": "אפשר לקבוע תור?",
        "timestamp": "2026-06-03T09:00:00"
      },
      {
        "sender": "bot",
        "text": "כן, איזה יום נוח לך?",
        "timestamp": "2026-06-03T09:00:08"
      }
    ]
  }
]
```

### JSONL

Each line must contain one conversation object:

```json
{"session_id":"s1","messages":[{"sender":"user","text":"אפשר חשבונית?"}]}
```

### CSV

```csv
session_id,sender,text,timestamp
s1,user,"אפשר חשבונית?",03/06/2026 09:00
s1,bot,"כן, נא לשלוח פרטים.",03/06/2026 09:00
```

## Run tests

```bash
pytest -q scripts
python -m compileall scripts/ -q
```

## File index

```text
SKILL.md
SKILL_HE.md
README.md
CHANGELOG.md
LICENSE
metadata.json
pyproject.toml
requirements-dev.txt
chat_data_analyzer_client.py
chat_data_analyzer_cli.py
references/api-reference.md
references/workflow-guide.md
references/troubleshooting.md
references/test-scenarios.md
references/migration-checklist.md
references/branding-audit.md
references/hebrew-qa-log.md
scripts/chat-data-analyzer-cli.py
scripts/test_chat_data_analyzer_client.py
scripts/examples/01_analyze_single_text.py
scripts/examples/02_analyze_json_dataset.py
scripts/examples/03_anonymize_before_export.py
scripts/examples/04_async_batch_analysis.py
scripts/examples/05_cli_end_to_end.py
scripts/examples/06_custom_intents.py
```

## Production cautions

- Treat labels as triage signals, not legal, accounting, tax, or privacy advice.
- Mask raw examples before broad sharing.
- Keep current Israeli regulatory and tax requirements outside classifier logic.
- Review samples manually before changing customer-facing scripts.
- Keep custom intent dictionaries versioned.
