# Land Registry Data Fetcher (Tabu)

Neutral package for retrieving, validating, structuring, and explaining Israeli Tabu land registry information about property ownership, encumbrances, mortgages, caveats, liens, leases, easements, shares, and parcel-level due-diligence signals.

Use it for Israeli small-business, freelancer, and consumer workflows: checking a storefront lease, reviewing a property purchase, assessing collateral, preparing a professional review pack, or converting a registry extract into a structured summary.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Run a local fixture lookup:

```bash
land-registry-tabu --mock-file scripts/fixtures/sample_parcel_response.json parcel --block 30001 --parcel 12 --subparcel 4
```

Use the installable module directly:

```python
from land_registry_tabu import FileJsonTransport, LandRegistryTabuClient, ParcelId, TabuClientConfig

client = LandRegistryTabuClient(
    TabuClientConfig(base_url="https://sandbox.example.internal.gov-adapter.local"),
    transport=FileJsonTransport("scripts/fixtures/sample_parcel_response.json"),
)
extract = client.get_by_parcel(ParcelId(30001, 12, 4))
print(extract.to_json())
```

Create an extract order, extract the returned ID, and use it in the next step:

```bash
CREATE_RESPONSE="$(land-registry-tabu   --mock-file scripts/fixtures/sample_parcel_response.json   --order-mock-file scripts/fixtures/sample_order_response.json   create-order --block 30001 --parcel 12 --subparcel 4   --payment-reference PAY-SANDBOX-0001)"

ORDER_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["order_id"])' <<< "$CREATE_RESPONSE")"

land-registry-tabu   --mock-file scripts/fixtures/sample_parcel_response.json   --order-mock-file scripts/fixtures/sample_order_response.json   order-status --order-id "$ORDER_ID"
```

Run tests and syntax checks:

```bash
pytest
python -m compileall scripts/ -q
```

## Environment

The CLI and examples read these variables:

| Variable | Purpose |
|---|---|
| `TABU_ENV` | Default environment, `sandbox` or `production` |
| `TABU_SANDBOX_BASE_URL` | Sandbox adapter base URL |
| `TABU_PRODUCTION_BASE_URL` | Production adapter base URL |
| `TABU_API_KEY` | Bearer token for the configured adapter |
| `TABU_PAYMENT_REFERENCE` | Payment reference for order examples |

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, edge cases, troubleshooting, anti-patterns, and checklist |
| `SKILL_HE.md` | Hebrew operating guide with Israeli professional terminology and local date/currency formatting |
| `src/land_registry_tabu/` | Installable Python package |
| `scripts/land_registry_tabu_client.py` | Underscored compatibility re-export |
| `scripts/land_registry_tabu_cli.py` | Script entry point |
| `scripts/test_land_registry_tabu_client.py` | Pytest suite |
| `scripts/examples/` | Runnable examples that accept `--env sandbox|production` |
| `scripts/fixtures/` | Local JSON fixtures |
| `references/api-reference.md` | API and regulation reference with examples and error tables |
| `references/workflow-guide.md` | End-to-end workflows |
| `references/troubleshooting.md` | Operational diagnostics |
| `references/test-scenarios.md` | Scenario list for QA |
| `references/migration-checklist.md` | Migration guidance |
| `references/branding-audit.md` | Neutrality and public-asset audit report |
| `references/hebrew-qa-log.md` | Hebrew quality review log |
| `CHANGELOG.md` | Version history |
| `LICENSE` | MIT license |

## Practical scope

Use the package to:

- Normalize block, parcel, and subparcel identifiers.
- Query a configurable adapter or local fixture.
- Parse Hebrew-key and English-key payloads.
- Mask Israeli personal IDs in summaries.
- Detect registered mortgages, caveats, liens, attachments, easements, and leases.
- Produce risk flags for professional review.
- Preserve raw payloads and timestamps for audit.

Web validation on 04/06/2026 confirmed the core Tabu extract and VAT reference claims in `references/verification-log.md`. Official service access, fees, authentication, and data availability can change. Keep endpoints, payment settings, and field mappings configurable, and verify production behavior through official channels before relying on live use.
