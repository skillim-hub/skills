from __future__ import annotations

import asyncio
import json
from pathlib import Path

from click.testing import CliRunner

from disaster_preparedness_guide import BusinessProfile, HouseholdProfile, PreparednessClient, UnknownHazardError, make_plan_id, validate_environment
from disaster_preparedness_guide.cli import cli

ROOT = Path(__file__).resolve().parents[1]


def test_lookup_missile_by_keyword():
    assert PreparednessClient().lookup('missile').key == 'missile'


def test_lookup_missile_by_category():
    assert PreparednessClient().lookup(1).key == 'missile'


def test_lookup_hebrew_earthquake():
    p = PreparednessClient().lookup('רעידת אדמה')
    assert p.key == 'earthquake'
    assert 'open' in ' '.join(p.immediate_actions + p.do_not).lower()


def test_lookup_hazmat_keyword():
    p = PreparednessClient().lookup('chemical plume')
    assert p.key == 'hazmat'
    assert 'basement' in ' '.join(p.do_not).lower()


def test_lookup_tsunami_hebrew():
    assert PreparednessClient().lookup('צונאמי').key == 'tsunami'


def test_lookup_radiological_category():
    assert PreparednessClient().lookup('5').key == 'radiological'


def test_lookup_terrorist_hebrew():
    assert PreparednessClient().lookup('חדירת מחבלים').key == 'terrorist_infiltration'


def test_lookup_unknown_raises():
    try:
        PreparednessClient().lookup('volcano')
    except UnknownHazardError:
        pass
    else:
        raise AssertionError('expected UnknownHazardError')


def test_list_hazards_contains_core():
    hazards = PreparednessClient().list_hazards()
    assert {'missile', 'earthquake', 'hazmat'} <= set(hazards)


def test_validate_environment_from_arg():
    assert validate_environment('production') == 'production'


def test_validate_environment_rejects_bad_value():
    try:
        validate_environment('staging')
    except ValueError:
        pass
    else:
        raise AssertionError('expected ValueError')


def test_environment_from_env_var(monkeypatch):
    monkeypatch.setenv('DPG_ENV', 'production')
    assert PreparednessClient().environment == 'production'


def test_make_plan_id_contains_type_and_env():
    assert make_plan_id('household', 'Haifa', 'sandbox').startswith('household-sandbox-')


def test_decide_earthquake_coastal_adds_tsunami():
    result = PreparednessClient().decide_action('earthquake', {'near_coast': True, 'has_mamad': True})
    assert 'earthquake_mamad_door_open' in result['risk_flags']
    assert any('tsunami' in a.lower() for a in result['immediate_actions'])


def test_decide_hazmat_basement_flag():
    result = PreparednessClient().decide_action('hazmat', {'in_basement': True})
    assert 'basement_may_be_unsafe_for_chemical_plume' in result['risk_flags']


def test_decide_missile_business_customer_guidance():
    result = PreparednessClient().decide_action('missile', {'business_open': True})
    assert any('customers' in a for a in result['immediate_actions'])


def test_hostile_aircraft_ten_minute_rule():
    protocol = PreparednessClient().lookup('drone')
    assert protocol.key == 'hostile_aircraft'
    assert '10 minutes' in protocol.shelter_time
    assert 'another alert' in protocol.shelter_time


def test_radiological_is_official_instruction_only():
    protocol = PreparednessClient().lookup('radiological')
    joined = ' '.join(protocol.immediate_actions + protocol.do_not)
    assert 'official' in joined.lower()
    assert 'iodine' in joined.lower()
    assert 'Remove contaminated outer clothing' not in joined


def test_household_plan_with_pets_and_children():
    plan = PreparednessClient().household_plan(HouseholdProfile(city='Haifa', people=4, pets=True, children=2))
    assert plan.plan_type == 'household'
    assert plan.plan_id
    assert any('pet' in item for item in plan.supplies)


def test_household_plan_accessibility_flag():
    plan = PreparednessClient().household_plan(HouseholdProfile(city='Jerusalem', people=2, accessibility_needs=True))
    assert 'accessibility_route_check_required' in plan.risk_flags


def test_household_plan_rejects_zero_people():
    try:
        PreparednessClient().household_plan(HouseholdProfile(city='Eilat', people=0))
    except ValueError:
        pass
    else:
        raise AssertionError('expected ValueError')


def test_business_capacity_flag():
    plan = PreparednessClient().business_plan(BusinessProfile(city='Ashdod', business_type='shop', employees=3, customers_peak=10, protected_space_capacity=8))
    assert 'capacity_exceeded' in plan.risk_flags


def test_business_chemicals_flag():
    plan = PreparednessClient().business_plan(BusinessProfile(city='Haifa', business_type='workshop', employees=2, stores_chemicals=True))
    assert 'hazmat_controls_required' in plan.risk_flags


def test_business_daily_revenue_record():
    plan = PreparednessClient().business_plan(BusinessProfile(city='Tel Aviv', business_type='studio', employees=1, daily_revenue_nis=850))
    assert any('850' in record for record in plan.records)


def test_create_plan_and_summarize():
    client = PreparednessClient(environment='sandbox')
    created = client.create_plan(HouseholdProfile(city='Haifa', people=4))
    summary = client.summarize_plan(created, created['id'])
    assert summary['id'] == created['id']


def test_summarize_rejects_wrong_id():
    client = PreparednessClient()
    created = client.create_plan(HouseholdProfile(city='Haifa', people=4))
    try:
        client.summarize_plan(created, 'wrong-id')
    except ValueError:
        pass
    else:
        raise AssertionError('expected ValueError')


def test_go_bag_business_pets_medications():
    items = PreparednessClient().go_bag(pets=True, business=True, medications=True)
    assert {'pet leash/carrier', 'insurance policy number', 'medications'} <= set(items)


def test_export_json_protocol(tmp_path):
    client = PreparednessClient()
    target = tmp_path / 'protocol.json'
    client.export_json(client.lookup('missile'), target)
    assert json.loads(target.read_text(encoding='utf-8'))['key'] == 'missile'


def test_export_json_plan(tmp_path):
    client = PreparednessClient()
    plan = client.household_plan(HouseholdProfile(city='Acre', people=1))
    target = tmp_path / 'plan.json'
    client.export_json(plan, target)
    assert json.loads(target.read_text(encoding='utf-8'))['plan_type'] == 'household'


def test_read_json(tmp_path):
    target = tmp_path / 'data.json'
    target.write_text('{"ok": true}', encoding='utf-8')
    assert PreparednessClient().read_json(target)['ok'] is True


def test_async_lookup():
    async def run():
        return await PreparednessClient().async_lookup('hazmat')
    assert asyncio.run(run()).key == 'hazmat'


def test_async_decide_action():
    async def run():
        return await PreparednessClient().async_decide_action('earthquake', {'near_coast': True})
    assert asyncio.run(run())['event'] == 'earthquake'


def test_async_household_plan():
    async def run():
        return await PreparednessClient().async_household_plan(HouseholdProfile(city='Netanya', people=3, near_coast=True))
    assert 'coastal_tsunami_awareness' in asyncio.run(run()).risk_flags


def test_async_business_plan():
    async def run():
        return await PreparednessClient().async_business_plan(BusinessProfile(city='Lod', business_type='clinic', employees=4, uses_gas=True))
    assert 'gas_shutdown_review_required' in asyncio.run(run()).risk_flags


def test_cli_lookup_json():
    result = CliRunner().invoke(cli, ['lookup', 'hazmat', '--json', '--env', 'production'])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload['key'] == 'hazmat' and payload['environment'] == 'production'


def test_cli_decide():
    result = CliRunner().invoke(cli, ['decide', 'earthquake', '--near-coast', '--has-mamad'])
    assert result.exit_code == 0
    assert 'earthquake_mamad_door_open' in json.loads(result.output)['risk_flags']


def test_cli_plan_household_output(tmp_path):
    out = tmp_path / 'household.json'
    result = CliRunner().invoke(cli, ['plan-household', '--city', 'Haifa', '--people', '4', '--pets', '--output', str(out)])
    assert result.exit_code == 0 and out.exists()
    assert json.loads(out.read_text(encoding='utf-8'))['plan_type'] == 'household'


def test_cli_plan_business_json():
    result = CliRunner().invoke(cli, ['plan-business', '--city', 'Ashdod', '--business-type', 'shop', '--employees', '3', '--customers-peak', '10', '--protected-space-capacity', '5'])
    assert result.exit_code == 0
    assert 'capacity_exceeded' in result.output


def test_cli_create_review_chain(tmp_path):
    out = tmp_path / 'created.json'
    runner = CliRunner()
    create = runner.invoke(cli, ['create-household-plan', '--city', 'Haifa', '--people', '4', '--output', str(out)])
    assert create.exit_code == 0
    plan_id = json.loads(create.output)['id']
    review = runner.invoke(cli, ['review-plan', '--plan-file', str(out), '--plan-id', plan_id])
    assert review.exit_code == 0
    assert json.loads(review.output)['id'] == plan_id


def test_cli_go_bag_json():
    result = CliRunner().invoke(cli, ['go-bag', '--pets', '--business', '--medications'])
    assert result.exit_code == 0
    assert 'insurance policy number' in json.loads(result.output)['items']


def test_metadata_version_is_210():
    metadata = json.loads((ROOT / 'metadata.json').read_text(encoding='utf-8'))
    assert metadata['version'] == '2.1.0'
    assert metadata['validated_with_web'] is True


def test_examples_support_env_and_json_dumps():
    for script in sorted((ROOT / 'scripts' / 'examples').glob('*.py')):
        text = script.read_text(encoding='utf-8')
        assert '--env' in text
        assert 'os.getenv' in text
        assert 'json.dumps' in text
        assert 'ensure_ascii=False' in text
        assert 'indent=2' in text
