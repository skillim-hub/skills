from __future__ import annotations
import json, os
from pathlib import Path
from typing import Optional
import click
from .client import BusinessProfile, HouseholdProfile, PreparednessClient, UnknownHazardError

@click.group(context_settings={'help_option_names': ['-h', '--help']})
def cli() -> None:
    """Offline preparedness CLI. Does not fetch live alerts."""

@cli.command()
@click.argument('query')
@click.option('--json-output', '--json', 'as_json', is_flag=True)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
def lookup(query: str, as_json: bool, environment: str) -> None:
    client=PreparednessClient(environment=environment)
    try: protocol=client.lookup(query)
    except UnknownHazardError as exc: raise click.ClickException(f'UNKNOWN_EVENT_TYPE: {exc}') from exc
    payload=protocol.to_dict(); payload['environment']=client.environment
    if as_json: click.echo(json.dumps(payload, ensure_ascii=False, indent=2)); return
    click.echo(f'{protocol.title_en} / {protocol.title_he}')
    click.echo(protocol.summary)
    click.echo('Immediate actions:')
    for action in protocol.immediate_actions: click.echo(f'- {action}')
    click.echo(f'Shelter/release: {protocol.shelter_time}')
    click.echo('Official current instructions override this CLI.')

@cli.command('decide')
@click.argument('event_type')
@click.option('--near-coast', is_flag=True)
@click.option('--has-mamad', is_flag=True)
@click.option('--can-exit-in-seconds', is_flag=True)
@click.option('--in-basement', is_flag=True)
@click.option('--business-open', is_flag=True)
@click.option('--accessibility-needs', is_flag=True)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
def decide(event_type: str, near_coast: bool, has_mamad: bool, can_exit_in_seconds: bool, in_basement: bool, business_open: bool, accessibility_needs: bool, environment: str) -> None:
    client=PreparednessClient(environment=environment)
    payload=client.decide_action(event_type, {'near_coast':near_coast,'has_mamad':has_mamad,'can_exit_in_seconds':can_exit_in_seconds,'in_basement':in_basement,'business_open':business_open,'accessibility_needs':accessibility_needs})
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))

@cli.command('plan-household')
@click.option('--city', required=True)
@click.option('--people', required=True, type=int)
@click.option('--protected-space', default='mamad', show_default=True)
@click.option('--pets', is_flag=True)
@click.option('--children', default=0, type=int)
@click.option('--older-adults', default=0, type=int)
@click.option('--accessibility-needs', is_flag=True)
@click.option('--near-coast', is_flag=True)
@click.option('--medications', is_flag=True)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
@click.option('--output', type=click.Path(path_type=Path))
def plan_household(city: str, people: int, protected_space: str, pets: bool, children: int, older_adults: int, accessibility_needs: bool, near_coast: bool, medications: bool, environment: str, output: Optional[Path]) -> None:
    client=PreparednessClient(environment=environment)
    profile=HouseholdProfile(city=city, people=people, protected_space=protected_space, pets=pets, children=children, older_adults=older_adults, accessibility_needs=accessibility_needs, near_coast=near_coast, medications=medications)
    payload=client.household_plan(profile).to_dict()
    if output: client.export_json(payload, output); click.echo(str(output))
    else: click.echo(json.dumps(payload, ensure_ascii=False, indent=2))

@cli.command('plan-business')
@click.option('--city', required=True)
@click.option('--business-type', required=True)
@click.option('--employees', required=True, type=int)
@click.option('--customers-peak', default=0, type=int)
@click.option('--protected-space-capacity', type=int)
@click.option('--stores-chemicals', is_flag=True)
@click.option('--uses-gas', is_flag=True)
@click.option('--keeps-customer-property', is_flag=True)
@click.option('--accessibility-needs', is_flag=True)
@click.option('--daily-revenue-nis', type=int)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
@click.option('--output', type=click.Path(path_type=Path))
def plan_business(city: str, business_type: str, employees: int, customers_peak: int, protected_space_capacity: Optional[int], stores_chemicals: bool, uses_gas: bool, keeps_customer_property: bool, accessibility_needs: bool, daily_revenue_nis: Optional[int], environment: str, output: Optional[Path]) -> None:
    client=PreparednessClient(environment=environment)
    profile=BusinessProfile(city=city, business_type=business_type, employees=employees, customers_peak=customers_peak, protected_space_capacity=protected_space_capacity, stores_chemicals=stores_chemicals, uses_gas=uses_gas, keeps_customer_property=keeps_customer_property, accessibility_needs=accessibility_needs, daily_revenue_nis=daily_revenue_nis)
    payload=client.business_plan(profile).to_dict()
    if output: client.export_json(payload, output); click.echo(str(output))
    else: click.echo(json.dumps(payload, ensure_ascii=False, indent=2))

@cli.command('create-household-plan')
@click.option('--city', required=True)
@click.option('--people', required=True, type=int)
@click.option('--protected-space', default='mamad', show_default=True)
@click.option('--pets', is_flag=True)
@click.option('--children', default=0, type=int)
@click.option('--older-adults', default=0, type=int)
@click.option('--accessibility-needs', is_flag=True)
@click.option('--near-coast', is_flag=True)
@click.option('--medications', is_flag=True)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
@click.option('--output', type=click.Path(path_type=Path), required=True)
def create_household_plan(city: str, people: int, protected_space: str, pets: bool, children: int, older_adults: int, accessibility_needs: bool, near_coast: bool, medications: bool, environment: str, output: Path) -> None:
    client=PreparednessClient(environment=environment)
    profile=HouseholdProfile(city=city, people=people, protected_space=protected_space, pets=pets, children=children, older_adults=older_adults, accessibility_needs=accessibility_needs, near_coast=near_coast, medications=medications)
    payload=client.create_plan(profile)
    client.export_json(payload, output)
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2))

@cli.command('review-plan')
@click.option('--plan-file', type=click.Path(path_type=Path), required=True)
@click.option('--plan-id', required=True)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
def review_plan(plan_file: Path, plan_id: str, environment: str) -> None:
    client=PreparednessClient(environment=environment)
    summary=client.summarize_plan(client.read_json(plan_file), plan_id)
    click.echo(json.dumps(summary, ensure_ascii=False, indent=2))

@cli.command('go-bag')
@click.option('--pets', is_flag=True)
@click.option('--business', is_flag=True)
@click.option('--medications', is_flag=True)
@click.option('--env', 'environment', type=click.Choice(['sandbox','production']), default=lambda: os.getenv('DPG_ENV','sandbox'))
def go_bag(pets: bool, business: bool, medications: bool, environment: str) -> None:
    client=PreparednessClient(environment=environment)
    click.echo(json.dumps({'environment': client.environment, 'items': client.go_bag(pets=pets, business=business, medications=medications)}, ensure_ascii=False, indent=2))

def main() -> None:
    cli()
