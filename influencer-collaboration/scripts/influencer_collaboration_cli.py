"""Command line interface for the influencer collaboration helper."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer

from influencer_collaboration_client import (
    CampaignMetric,
    InfluencerCollaborationClient,
    brief_from_dict,
    load_profiles_csv,
    profile_from_dict,
    read_json,
)

app = typer.Typer(help="Plan, score, and track Israeli influencer collaborations.")
client = InfluencerCollaborationClient()


def _dump(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)



@app.command("create-brief")
def create_brief(
    business_name: str = typer.Option(..., "--business-name", help="Business name."),
    product_or_service: str = typer.Option(..., "--product-or-service", help="Offer description."),
    goal: str = typer.Option("awareness", "--goal", help="awareness, leads, sales, foot_traffic, or content_reuse."),
    target_location: list[str] = typer.Option(["Israel"], "--target-location", help="Target city or region. Repeat for several locations."),
    target_segment: list[str] = typer.Option(["general"], "--target-segment", help="Target segment. Repeat for several segments."),
    budget_ils: float = typer.Option(..., "--budget-ils", help="Budget in ₪."),
    start_date: str = typer.Option(..., "--start-date", help="YYYY-MM-DD or DD/MM/YYYY."),
    end_date: str = typer.Option(..., "--end-date", help="YYYY-MM-DD or DD/MM/YYYY."),
    deliverable: list[str] = typer.Option(["story"], "--deliverable", help="Deliverable. Repeat for several deliverables."),
    storage_dir: Path = typer.Option(Path(".ich/briefs"), "--storage-dir", help="Directory for saved briefs."),
) -> None:
    """Create and store a campaign brief, then print its identifier."""
    brief_id = uuid.uuid4().hex[:12]
    storage_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": brief_id,
        "business_name": business_name,
        "product_or_service": product_or_service,
        "goal": goal,
        "target_locations": target_location,
        "target_segments": target_segment,
        "budget_ils": budget_ils,
        "start_date": start_date,
        "end_date": end_date,
        "deliverables": deliverable,
    }
    path = storage_dir / f"{brief_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    typer.echo(_dump({"id": brief_id, "path": str(path), "created": True}))


@app.command("plan-by-brief-id")
def plan_by_brief_id(
    brief_id: str = typer.Argument(..., help="Brief identifier returned by create-brief."),
    profiles_csv: Path = typer.Argument(..., exists=True, readable=True, help="CSV file of creator profiles."),
    storage_dir: Path = typer.Option(Path(".ich/briefs"), "--storage-dir", help="Directory for saved briefs."),
    max_creators: int = typer.Option(5, "--max-creators", min=1, help="Maximum shortlisted creators."),
) -> None:
    """Build a plan using a stored campaign brief identifier."""
    path = storage_dir / f"{brief_id}.json"
    if not path.exists():
        raise typer.BadParameter(f"brief id not found: {brief_id}")
    profiles = load_profiles_csv(profiles_csv)
    brief = brief_from_dict(read_json(path))
    typer.echo(_dump(client.build_plan(profiles, brief, max_creators=max_creators)))


@app.command()
def score(
    profile_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON profile file."),
    brief_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON campaign brief file."),
) -> None:
    """Score a single creator against a campaign brief."""
    profile = profile_from_dict(read_json(profile_file))
    brief = brief_from_dict(read_json(brief_file))
    typer.echo(_dump(asdict(client.score_profile(profile, brief))))


@app.command()
def rank(
    profiles_csv: Path = typer.Argument(..., exists=True, readable=True, help="CSV file of creator profiles."),
    brief_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON campaign brief file."),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Maximum number of profiles to return."),
) -> None:
    """Rank creators from a CSV file."""
    profiles = load_profiles_csv(profiles_csv)
    brief = brief_from_dict(read_json(brief_file))
    typer.echo(_dump([asdict(item) for item in client.rank_profiles(profiles, brief, limit=limit)]))


@app.command()
def outreach(
    profile_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON profile file."),
    brief_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON campaign brief file."),
    tone: str = typer.Option("professional", "--tone", help="professional, warm, or direct."),
) -> None:
    """Generate Hebrew outreach copy."""
    profile = profile_from_dict(read_json(profile_file))
    brief = brief_from_dict(read_json(brief_file))
    typer.echo(_dump(asdict(client.generate_outreach(profile, brief, tone=tone))))


@app.command()
def disclosure(
    text: str = typer.Argument(..., help="Caption or script text."),
    required: str = typer.Option("פרסומת", "--required", help="Required Hebrew disclosure term."),
) -> None:
    """Validate commercial disclosure wording."""
    ok, issues = client.validate_disclosure(text, required_disclosure=required)
    typer.echo(_dump({"valid": ok, "issues": issues}))


@app.command()
def plan(
    profiles_csv: Path = typer.Argument(..., exists=True, readable=True, help="CSV file of creator profiles."),
    brief_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON campaign brief file."),
    max_creators: int = typer.Option(5, "--max-creators", min=1, help="Maximum shortlisted creators."),
) -> None:
    """Build a campaign plan."""
    profiles = load_profiles_csv(profiles_csv)
    brief = brief_from_dict(read_json(brief_file))
    typer.echo(_dump(client.build_plan(profiles, brief, max_creators=max_creators)))


@app.command()
def summarize(
    metrics_file: Path = typer.Argument(..., exists=True, readable=True, help="JSON array of performance rows."),
) -> None:
    """Summarize campaign performance."""
    rows = read_json(metrics_file)
    metrics = [
        CampaignMetric(
            handle=str(row["handle"]),
            spend_ils=float(row.get("spend_ils", 0)),
            impressions=int(row.get("impressions", 0)),
            views=int(row.get("views", 0)),
            clicks=int(row.get("clicks", 0)),
            leads=int(row.get("leads", 0)),
            sales=int(row.get("sales", 0)),
            revenue_ils=float(row.get("revenue_ils", 0)),
            date_reported=brief_from_dict(
                {
                    "business_name": "tmp",
                    "product_or_service": "tmp",
                    "budget_ils": 1,
                    "start_date": row.get("date_reported", "2026-01-01"),
                    "end_date": row.get("date_reported", "2026-01-01"),
                    "target_locations": ["Israel"],
                    "target_segments": ["general"],
                }
            ).start_date,
        )
        for row in rows
    ]
    typer.echo(_dump(asdict(client.summarize_metrics(metrics))))


def main() -> None:
    """Run the CLI."""
    app()


if __name__ == "__main__":
    main()
