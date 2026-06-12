from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer

from .client import ReferralProgramManager

app = typer.Typer(help="Manage referral programs, referrals, rewards, and payout exports.")


def _emit(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def load_manager(state: Path) -> ReferralProgramManager:
    return ReferralProgramManager.load_json(state)


def save_manager(manager: ReferralProgramManager, state: Path) -> None:
    manager.save_json(state)


@app.command("init-state")
def init_state(state: Path = typer.Option(..., help="JSON state file path.")) -> None:
    """Create an empty state file."""
    manager = ReferralProgramManager()
    save_manager(manager, state)
    _emit({"state": str(state), "status": "initialized"})


@app.command("create-program")
def create_program(
    state: Path = typer.Option(...),
    program_id: str = typer.Option(...),
    name: str = typer.Option(...),
    reward_type: str = typer.Option("credit"),
    reward_amount: float = typer.Option(...),
    qualifying_action: str = typer.Option(...),
    cooldown_days: int = typer.Option(14),
    max_rewards: int = typer.Option(5),
    minimum_order: float = typer.Option(0.0),
    terms_version: str = typer.Option("v1"),
) -> None:
    """Create or update a referral program."""
    manager = load_manager(state)
    program = manager.create_program(
        program_id=program_id,
        name=name,
        reward_type=reward_type,
        reward_amount_ils=reward_amount,
        qualifying_action=qualifying_action,
        cooldown_days=cooldown_days,
        max_rewards_per_customer=max_rewards,
        minimum_order_ils=minimum_order,
        terms_version=terms_version,
    )
    save_manager(manager, state)
    _emit(
        {
            "status": "saved",
            "program_id": program.program_id,
            "reward_type": program.reward_type.value,
            "reward_amount_ils": str(program.reward_amount_ils),
            "terms_version": program.terms_version,
        }
    )


@app.command("add-customer")
def add_customer(
    state: Path = typer.Option(...),
    customer_id: str = typer.Option(...),
    name: str = typer.Option(...),
    email: str = typer.Option(...),
    phone: str = typer.Option(...),
    marketing_consent: bool = typer.Option(False, "--marketing-consent/--no-marketing-consent"),
    existing_customer: bool = typer.Option(False, "--existing-customer/--new-customer"),
    employee: bool = typer.Option(False, "--employee/--not-employee"),
    vat_or_id: Optional[str] = typer.Option(None),
) -> None:
    """Add or update a customer."""
    manager = load_manager(state)
    customer = manager.add_customer(
        customer_id=customer_id,
        name=name,
        email=email,
        phone=phone,
        consent_marketing=marketing_consent,
        is_existing_customer=existing_customer,
        is_employee=employee,
        vat_or_id=vat_or_id,
    )
    save_manager(manager, state)
    _emit({"status": "saved", "customer_id": customer.customer_id, "phone": customer.phone})


@app.command("link")
def link(
    state: Path = typer.Option(...),
    program_id: str = typer.Option(...),
    customer_id: str = typer.Option(...),
    base_url: str = typer.Option(...),
) -> None:
    """Generate a referral link."""
    manager = load_manager(state)
    referral_link = manager.generate_referral_link(program_id, customer_id, base_url)
    _emit({"program_id": program_id, "customer_id": customer_id, "referral_link": referral_link})


@app.command("register")
def register(
    state: Path = typer.Option(...),
    program_id: str = typer.Option(...),
    referrer_id: str = typer.Option(...),
    referred_customer_id: str = typer.Option(...),
    source: str = typer.Option("manual"),
) -> None:
    """Register a referral event."""
    manager = load_manager(state)
    event = manager.register_referral(program_id, referrer_id, referred_customer_id, source)
    save_manager(manager, state)
    _emit(
        {
            "status": event.status.value,
            "event_id": event.event_id,
            "program_id": event.program_id,
            "referral_code": event.referral_code,
            "fraud_score": event.fraud_score,
            "review_reason": event.review_reason,
        }
    )


@app.command("qualify")
def qualify(
    state: Path = typer.Option(...),
    event_id: str = typer.Option(...),
    invoice: str = typer.Option(...),
    order_amount: float = typer.Option(0.0),
) -> None:
    """Mark a referral as qualified with invoice evidence."""
    manager = load_manager(state)
    event = manager.qualify_referral(event_id, evidence={"invoice": invoice}, order_amount_ils=order_amount)
    save_manager(manager, state)
    _emit({"status": event.status.value, "event_id": event.event_id, "qualified_at": event.qualified_at})


@app.command("approve")
def approve(
    state: Path = typer.Option(...),
    event_id: str = typer.Option(...),
    actor: str = typer.Option("owner"),
    tax_treatment: str = typer.Option("unclassified"),
    force: bool = typer.Option(False, "--force/--no-force"),
) -> None:
    """Approve a qualified reward."""
    manager = load_manager(state)
    reward = manager.approve_reward(event_id, actor=actor, tax_treatment=tax_treatment, force=force)
    save_manager(manager, state)
    _emit(
        {
            "status": reward.status.value,
            "reward_id": reward.reward_id,
            "event_id": reward.event_id,
            "amount_ils": str(reward.amount_ils),
            "tax_treatment": reward.tax_treatment,
        }
    )


@app.command("export-rewards")
def export_rewards(
    state: Path = typer.Option(...),
    output: Path = typer.Option(...),
    status: Optional[str] = typer.Option(None),
) -> None:
    """Export rewards to CSV."""
    manager = load_manager(state)
    manager.export_rewards_csv(output, status=status)
    _emit({"status": "exported", "output": str(output)})


@app.command("scenario")
def scenario(state: Path = typer.Option(...)) -> None:
    """Create a runnable demo scenario."""
    from .client import create_demo_manager

    manager = create_demo_manager()
    save_manager(manager, state)
    _emit({"status": "saved", "state": str(state), "reward_count": len(manager.rewards)})


def main() -> None:
    app()


if __name__ == "__main__":
    main()
