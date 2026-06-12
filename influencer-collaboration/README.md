# Influencer Collaboration Helper

A local, installable helper for Israeli influencer collaboration workflows. Use it to score creators, create Hebrew outreach, validate commercial disclosure wording, plan campaigns, and summarize performance.

## Installation

From the extracted project directory:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Verify installation:

```bash
python -c "from influencer_collaboration_client import InfluencerCollaborationClient; print(InfluencerCollaborationClient().__class__.__name__)"
```

Run tests:

```bash
pytest
python -m compileall scripts/ -q
```

## Quick start

Create a sample `profiles.csv` file:

```csv
handle,display_name,platform,niche,followers,avg_views,avg_likes,avg_comments,location,audience_israel_pct
haifa_food,דנה,instagram,אוכל בחיפה,18000,9000,620,80,חיפה,0.91
parents_north,ליאת,instagram,הורות וילדים בצפון,31000,14000,900,120,קריות,0.93
```

Create a campaign brief and extract the identifier from the create response:

```bash
CREATE_RESPONSE=$(influencer-collaboration create-brief \
  --business-name "קפה שכונתי" \
  --product-or-service "תפריט בוקר חדש" \
  --goal foot_traffic \
  --target-location "חיפה" \
  --target-segment food \
  --budget-ils 6500 \
  --start-date 10/06/2026 \
  --end-date 25/06/2026 \
  --deliverable reel \
  --deliverable story)

BRIEF_ID=$(CREATE_RESPONSE="$CREATE_RESPONSE" python -c 'import json, os; print(json.loads(os.environ["CREATE_RESPONSE"])["id"])')
echo "$BRIEF_ID"
```

Use the extracted identifier in the next command:

```bash
influencer-collaboration plan-by-brief-id "$BRIEF_ID" profiles.csv --max-creators 2
```

Alternative without shell variables:

```bash
printf '%s\n' "$CREATE_RESPONSE" > create-response.json
BRIEF_ID=$(python -c 'import json; print(json.load(open("create-response.json", encoding="utf-8"))["id"])')
influencer-collaboration plan-by-brief-id "$BRIEF_ID" profiles.csv
```

## Python quick start

```python
from datetime import date
from dataclasses import asdict
import json

from influencer_collaboration_client import (
    CampaignBrief,
    CollaborationGoal,
    InfluencerCollaborationClient,
    InfluencerProfile,
    MarketSegment,
    Platform,
)

client = InfluencerCollaborationClient()

profile = InfluencerProfile(
    handle="haifa_food",
    display_name="דנה",
    platform=Platform.INSTAGRAM,
    niche="אוכל בחיפה",
    followers=18000,
    avg_views=9000,
    avg_likes=620,
    avg_comments=80,
    location="חיפה",
    audience_israel_pct=0.91,
)

brief = CampaignBrief(
    business_name="קפה שכונתי",
    product_or_service="תפריט בוקר חדש",
    goal=CollaborationGoal.FOOT_TRAFFIC,
    target_locations=["חיפה"],
    target_segments=[MarketSegment.FOOD],
    budget_ils=6500,
    start_date=date(2026, 6, 10),
    end_date=date(2026, 6, 25),
    deliverables=["reel", "story"],
)

score = client.score_profile(profile, brief)
print(json.dumps(asdict(score), ensure_ascii=False, indent=2))
```

## CLI commands

| Command | Purpose |
|---|---|
| `create-brief` | Store a brief locally and return an identifier |
| `plan-by-brief-id` | Build a plan using a stored brief identifier |
| `score` | Score one profile JSON against one brief JSON |
| `rank` | Rank profiles from CSV |
| `outreach` | Generate Hebrew outreach copy |
| `disclosure` | Validate Hebrew commercial disclosure wording |
| `plan` | Build a plan from CSV and a brief file |
| `summarize` | Summarize performance rows |

## Examples

Run example scripts after installation:

```bash
python scripts/examples/01_discover_and_score.py --env sandbox
python scripts/examples/02_generate_outreach.py --env sandbox
python scripts/examples/03_validate_disclosure.py --env sandbox
python scripts/examples/04_campaign_plan.py --env sandbox
python scripts/examples/05_monthly_report.py --env sandbox
```

Each example reads environment variables and prints JSON using `ensure_ascii=False` and `indent=2`.

Common environment variables:

| Variable | Purpose |
|---|---|
| `ICH_ENV` | Default example environment |
| `ICH_SANDBOX_BUSINESS_NAME` | Sandbox business name |
| `ICH_SANDBOX_PRODUCT` | Sandbox product or service |
| `ICH_SANDBOX_BUDGET_ILS` | Sandbox budget in ₪ |
| `ICH_PRODUCTION_BUSINESS_NAME` | Production business name |
| `ICH_PRODUCTION_PRODUCT` | Production product or service |
| `ICH_PRODUCTION_BUDGET_ILS` | Production budget in ₪ |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide |
| `SKILL_HE.md` | Hebrew operating guide localized for Israel |
| `references/api-reference.md` | Data schemas, examples, Israeli regulation checklist, and integration mapping |
| `references/workflow-guide.md` | End-to-end campaign workflows |
| `references/troubleshooting.md` | Failure-mode guide |
| `references/test-scenarios.md` | Manual QA scenarios |
| `references/migration-checklist.md` | Upgrade and migration steps |
| `references/branding-audit.md` | Branding and public Markdown audit |
| `references/hebrew-qa-log.md` | Hebrew quality assurance log |
| `references/verification-log.md` | Web validation log for Israeli rates, regulatory sources, and applicability checks |
| `scripts/influencer_collaboration_client.py` | Typed sync and async implementation |
| `scripts/influencer_collaboration_cli.py` | Importable Typer CLI implementation |
| `scripts/influencer-collaboration-cli.py` | Direct execution wrapper |
| `scripts/test_influencer_collaboration_client.py` | Pytest suite |
| `scripts/examples/` | Runnable scenario examples |
| `metadata.json` | Skill metadata |
| `pyproject.toml` | Installable Python project configuration |
| `requirements-dev.txt` | Development and test dependencies |

## Operational notes

- Treat scoring as a decision aid, not an automatic approval.
- Require clear Hebrew commercial disclosure before publication.
- Use one coupon code or tracked link per creator.
- Keep payment, product value, usage rights, exclusivity, and reporting in separate written lines.
- Confirm tax, privacy, and regulated-category issues with qualified professionals. The verification log confirms the standard VAT rate as 18% as of 03/06/2026, but production use should still recheck official sources before launch.
