# Migration checklist

Use this checklist when moving from an older package version or a manual spreadsheet workflow to this package.

## Python file layout

- Replace imports from a hyphenated client filename with `influencer_collaboration_client`.
- Do not import from `scripts/influencer-collaboration-client.py`; that file is intentionally absent.
- Install the project with `pip install -e .`.
- Import the module directly:

```python
from influencer_collaboration_client import InfluencerCollaborationClient
```

## CLI changes

- Use the installed command `influencer-collaboration`.
- Direct script execution remains available through `scripts/influencer-collaboration-cli.py`.
- Keep the real CLI implementation in `scripts/influencer_collaboration_cli.py`.

## README install changes

Use this sequence:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Data changes

| Old field | New field | Action |
|---|---|---|
| `username` | `handle` | Strip URL and leading symbol |
| `category` | `niche` | Keep free text |
| `country_il_percent` | `audience_israel_pct` | Convert 91 percent to 0.91 |
| `price` | `quoted_fee_ils` or budget allocation | Keep ₪ values as numbers |
| `post_type` | `deliverables` | Use a list such as `reel`, `story` |
| `campaign_start` | `start_date` | Prefer DD/MM/YYYY in examples |
| `campaign_end` | `end_date` | Prefer DD/MM/YYYY in examples |

## Workflow changes

- Replace follower-only sorting with score-based ranking.
- Add Israeli audience share to every shortlist decision.
- Add exact Hebrew disclosure wording before approval.
- Add written usage rights before reposting creator content.
- Add one coupon code or tracked link per creator.
- Add screenshot collection for stories.
- Add invoice or receipt status to payment tracking.
- Add privacy review when collecting leads.

## Testing changes

- Install development requirements.
- Run `pytest`.
- Run `python -m compileall scripts/ -q`.
- Verify all examples run with `--env sandbox`.

## Documentation changes

- Use `SKILL.md` for English workflows.
- Use `SKILL_HE.md` for Hebrew workflows.
- Use `references/api-reference.md` for schema, regulation checklist, and integration mapping.
- Use `references/workflow-guide.md` for end-to-end operations.
- Use `references/troubleshooting.md` for failure modes.
- Use `references/test-scenarios.md` for manual QA.

## Backward compatibility notes

- Keep old CSV exports as source data, but rename headers before import.
- Recalculate scores after adding Israeli audience share.
- Reconfirm disclosure and usage rights for any active campaign before renewal.
- Do not assume old outreach templates contain enough legal or operational detail.
