"""Command line interface for the local claim tracker."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from .client import (
    ClaimStatus,
    HealthInsuranceClaimTrackerClient,
    PolicyType,
    format_israeli_date,
)

app = typer.Typer(help="Track Israeli health-insurance claims and reimbursements.")
_state: dict[str, str] = {}


def _storage_path() -> Path:
    value = _state.get("storage") or os.environ.get("HICT_STORAGE_PATH") or str(Path.home() / ".hict" / "claims.json")
    return Path(value).expanduser()


def _client() -> HealthInsuranceClaimTrackerClient:
    return HealthInsuranceClaimTrackerClient(_storage_path())


def _print(data: object) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


@app.callback()
def main(
    env: str = typer.Option("sandbox", "--env", help="Execution environment: sandbox or production."),
    storage: Optional[Path] = typer.Option(None, "--storage", help="Path to the local JSON store."),
) -> None:
    if env not in {"sandbox", "production"}:
        raise typer.BadParameter("env must be sandbox or production")
    _state["env"] = env
    if storage:
        _state["storage"] = str(storage)


@app.command()
def create(
    claimant_reference: str = typer.Option(..., "--claimant-reference"),
    policy_type: PolicyType = typer.Option(PolicyType.PRIVATE, "--policy-type"),
    provider: str = typer.Option(..., "--provider"),
    service_date: str = typer.Option(..., "--service-date", help="YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY."),
    submission_date: str = typer.Option(..., "--submission-date", help="YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY."),
    amount: str = typer.Option(..., "--amount"),
    description: str = typer.Option(..., "--description"),
    channel: str = typer.Option("", "--channel"),
    service_kind: str = typer.Option("", "--service-kind"),
    follow_up_date: Optional[str] = typer.Option(None, "--follow-up-date"),
) -> None:
    claim = _client().create_claim(
        claimant_reference=claimant_reference,
        policy_type=policy_type,
        provider=provider,
        service_date=service_date,
        submission_date=submission_date,
        amount_claimed_ils=amount,
        description=description,
        channel=channel,
        service_kind=service_kind,
        follow_up_date=follow_up_date,
    )
    _print(claim.to_dict())


@app.command("show")
def show_claim(claim_id: str) -> None:
    _print(_client().get_claim(claim_id).to_dict())


@app.command("list")
def list_claims(
    status: Optional[ClaimStatus] = typer.Option(None, "--status"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    overdue_only: bool = typer.Option(False, "--overdue-only"),
) -> None:
    claims = _client().list_claims(status=status, provider=provider, overdue_only=overdue_only)
    _print([claim.to_dict(redact=True) for claim in claims])


@app.command("status")
def status_claim(claim_id: str, status: ClaimStatus, note: str = typer.Option("", "--note")) -> None:
    _print(_client().update_claim_status(claim_id, status, note=note).to_dict())


@app.command("document")
def add_document(
    claim_id: str,
    name: str = typer.Option(..., "--name"),
    document_type: str = typer.Option(..., "--document-type"),
    received: bool = typer.Option(True, "--received/--missing"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    _print(_client().add_document(claim_id, name=name, document_type=document_type, received=received, notes=notes).to_dict())


@app.command("reimburse")
def reimburse(
    claim_id: str,
    amount: str = typer.Option(..., "--amount"),
    paid_date: str = typer.Option(..., "--paid-date"),
    payer: str = typer.Option(..., "--payer"),
    reference: str = typer.Option("", "--reference"),
) -> None:
    _print(_client().add_reimbursement(claim_id, amount_ils=amount, paid_date=paid_date, payer=payer, reference=reference).to_dict())


@app.command("follow-up")
def follow_up(claim_id: str, follow_up_date: str = typer.Option(..., "--follow-up-date")) -> None:
    claim = _client().set_follow_up(claim_id, follow_up_date)
    _print({"id": claim.id, "follow_up_date": format_israeli_date(claim.follow_up_date)})


@app.command("summary")
def summary() -> None:
    _print(_client().summary())


@app.command("export-csv")
def export_csv(path: Path) -> None:
    output = _client().export_csv(path)
    _print({"path": str(output)})


@app.command("import-csv")
def import_csv(path: Path) -> None:
    claims = _client().import_csv(path)
    _print({"imported": len(claims), "ids": [claim.id for claim in claims]})


if __name__ == "__main__":
    app()
