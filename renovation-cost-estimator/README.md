# Renovation Cost Estimator

Estimate Israeli renovation budgets for consumers, freelancers, and small businesses using local per-meter, per-room, and trade-level planning benchmarks.

## Install

```bash
cd renovation-cost-estimator
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
cd renovation-cost-estimator
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start with chained project id

Create a project, extract the id from the create response, and use it in the next estimate step.

```bash
CREATE_RESPONSE=$(renovation-cost-estimator create \
  --env sandbox \
  --project-name "Clinic fit-out" \
  --city "Tel Aviv" \
  --property-type clinic \
  --area-sqm 38 \
  --scope-level commercial_fitout \
  --finish-level standard \
  --no-include-vat)

PROJECT_ID=$(printf '%s' "$CREATE_RESPONSE" | python -c "import json,sys; print(json.load(sys.stdin)['id'])")

renovation-cost-estimator estimate --env sandbox --project-id "$PROJECT_ID" --json
```

## Direct CLI use

```bash
renovation-cost-estimator scenario clinic --env sandbox
renovation-cost-estimator benchmarks
renovation-cost-estimator validate project.json
```

Estimate without storing:

```bash
renovation-cost-estimator estimate \
  --env sandbox \
  --city "Tel Aviv" \
  --property-type clinic \
  --area-sqm 38 \
  --scope-level commercial_fitout \
  --finish-level standard \
  --no-include-vat \
  --json
```

## Python quick start

```python
from renovation_cost_estimator import RenovationCostEstimatorClient

client = RenovationCostEstimatorClient()
record = client.create_project({
    "project_name": "Clinic fit-out",
    "city": "Tel Aviv",
    "property_type": "clinic",
    "area_sqm": 38,
    "scope_level": "commercial_fitout",
    "finish_level": "standard",
    "requires_business_license": True,
    "commercial_public_access": True,
    "include_vat": False
}, environment="sandbox")

result = client.estimate_by_id(record.id, environment="sandbox")
print(result.to_json())
```

## Environment variables

Examples and CLI options can read these values:

| Variable | Purpose |
|---|---|
| RENOVATION_CITY | default city |
| RENOVATION_PROPERTY_TYPE | apartment, office, shop, clinic |
| RENOVATION_AREA_SQM | area in square meters |
| RENOVATION_SCOPE_LEVEL | cosmetic, partial, full, shell, office_fitout, retail_fitout, commercial_fitout |
| RENOVATION_FINISH_LEVEL | basic, standard, premium, luxury |
| RENOVATION_INCLUDE_VAT | true or false |
| RENOVATION_VAT_RATE | decimal VAT rate |
| RENOVATION_ESTIMATOR_STORE | local project store directory |

## File index

| Path | Purpose |
|---|---|
| SKILL.md | English guide |
| SKILL_HE.md | Hebrew guide |
| references/api-reference.md | Israeli source and regulation reference |
| references/workflow-guide.md | end-to-end workflows |
| references/document-workflows.md | document templates |
| references/troubleshooting.md | troubleshooting |
| references/test-scenarios.md | concrete scenarios |
| references/migration-checklist.md | upgrade checklist |
| references/branding-audit.md | branding, credit, visual asset, and emoji audit |
| references/hebrew-qa-log.md | Hebrew quality-assurance log |
| references/verification-log.md | web-validated source log |
| renovation_cost_estimator/client.py | typed sync and async implementation |
| renovation_cost_estimator/cli.py | Typer CLI |
| scripts/renovation-cost-estimator-cli.py | executable wrapper for installed environments |
| scripts/test_renovation_cost_estimator_client.py | pytest suite |
| scripts/examples | runnable examples |

## Tests

```bash
python -m pytest scripts/test_renovation_cost_estimator_client.py -q
python -m compileall scripts/ -q
```

## Limitations

Benchmarks are planning ranges, not binding quotes. Verify VAT, official indices, permits, business licensing, accessibility, fire safety, lease constraints, and licensed-trade requirements before construction.


## Official-source boundary

Official sources validate VAT, CBS index data, licensing, permits, accessibility, fire safety, health, waste, asbestos, and standards. The package benchmark tables are planning heuristics and must be replaced with current written quotes for binding decisions.
