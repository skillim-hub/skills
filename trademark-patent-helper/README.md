# Trademark & Patent Filing Helper

A bilingual skill package for preparing Israeli trademark and patent filing materials for use with the Israel Patent Office (רשות הפטנטים).

The package helps Israeli small businesses, freelancers, startups, importers, creators, and consumers collect facts, classify trademark goods/services, prepare patent invention disclosures, identify risk, and troubleshoot filing workflows.

This package does not submit filings and does not provide legal advice. Verify current official forms, fees, deadlines, classifications, and portal behavior on the Israel Patent Office website before filing.

## File index

```text
SKILL.md                                       English skill guide
SKILL_HE.md                                    Hebrew skill guide
trademark_patent_helper/                       Installable Python package
references/api-reference.md                    Official-source and structured helper reference
references/workflow-guide.md                   End-to-end workflows
references/document-workflows.md               Document packet templates
references/troubleshooting.md                  Practical troubleshooting guide
references/test-scenarios.md                   Validation scenarios
references/migration-checklist.md              Upgrade checklist
references/branding-audit.md                   Branding and attribution audit
references/hebrew-qa-log.md                    Hebrew quality-assurance log
references/verification-log.md                 Web validation log
scripts/trademark_patent_helper_client.py      Compatibility import module
scripts/trademark-patent-helper-cli.py         CLI script wrapper
scripts/test_trademark_patent_helper_client.py Pytest suite
scripts/examples/                              Runnable examples
metadata.json                                  Skill metadata
CHANGELOG.md                                   Keep-a-Changelog history
LICENSE                                        MIT license
pyproject.toml                                 Python project config
requirements-dev.txt                           Development dependencies
```

## Install for local testing

```bash
cd trademark-patent-helper
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
cd trademark-patent-helper
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained local request ID

Create a local assessment record and capture the generated ID:

```bash
CREATE_RESPONSE="$(trademark-patent-helper create examples/sample-trademark.json --env sandbox --format json)"
REQUEST_ID="$(python -c 'import json, os; print(json.loads(os.environ["CREATE_RESPONSE"])["request_id"])')"
trademark-patent-helper show "$REQUEST_ID" --env sandbox --format markdown
```

The `create` command stores a local record only. It does not submit anything to רשות הפטנטים.

## Other commands

Print a trademark template:

```bash
trademark-patent-helper template trademark
```

Assess a trademark request without saving it:

```bash
trademark-patent-helper assess examples/sample-trademark.json --env sandbox --format markdown
```

Assess a patent request asynchronously:

```bash
trademark-patent-helper assess examples/sample-patent.json --env sandbox --format json --async-mode
```

Classify a plain-language description:

```bash
trademark-patent-helper intake "technical invention with pressure sensor and controller" --env sandbox --format json
```

Run tests:

```bash
pytest -q
python -m compileall scripts/ -q
```

## JSON example

```json
{
  "kind": "trademark",
  "applicant_name": "Example Ltd.",
  "mark_text": "ZAVILO",
  "mark_type": "word",
  "classes": [
    {"class_no": 25, "items": ["clothing", "shirts", "hats"]},
    {"class_no": 35, "items": ["online retail store services featuring clothing"]}
  ]
}
```

## Python example

```python
from trademark_patent_helper import FilingHelperClient

payload = {
    "kind": "trademark",
    "mark_text": "ZAVILO",
    "classes": [{"class_no": 25, "items": ["clothing"]}],
}

print(FilingHelperClient(environment="sandbox").assess(payload).to_markdown())
```

## Runnable examples

Each example reads environment variables and accepts `--env sandbox|production`.

```bash
IPO_APPLICANT_NAME="Example Ltd." IPO_MARK_TEXT="NUNA CAFÉ" python scripts/examples/01_trademark_cafe.py --env sandbox
IPO_APPLICANT_NAME_HE="דנה לוי" python scripts/examples/06_hebrew_trademark.py --env sandbox
```

## Practical use

Use the English or Hebrew guide to run a structured intake. Then use the reference workflows to create filing packets and evidence folders. Use the CLI to validate common risks and produce a structured assessment.

## Important cautions

- Trademark and patent rights are territorial.
- Israeli filing does not automatically protect abroad.
- Public disclosure may damage patent rights.
- Descriptive trademarks are often difficult to register broadly.
- Applicant ownership must be correct before filing.
- Current official requirements can change; verify before filing.
