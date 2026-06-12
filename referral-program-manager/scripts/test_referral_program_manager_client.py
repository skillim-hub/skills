from __future__ import annotations

import csv
import hashlib
import hmac
import json
import subprocess
import sys
from pathlib import Path

import pytest

import referral_program_manager as rpm


def manager_with_program(cooldown_days=0, reward_type="credit", minimum_order=0):
    m = rpm.ReferralProgramManager()
    m.create_program(
        program_id="p1",
        name="Test",
        reward_type=reward_type,
        reward_amount_ils=50,
        qualifying_action="paid",
        cooldown_days=cooldown_days,
        minimum_order_ils=minimum_order,
    )
    m.add_customer("c1", "Dana", "dana@example.co.il", "050-1234567", True)
    m.add_customer("c2", "Noa", "noa@example.co.il", "052-7654321", True)
    return m


def test_package_import_exposes_manager():
    assert rpm.ReferralProgramManager.__name__ == "ReferralProgramManager"


def test_phone_normalization_local():
    assert rpm.normalize_israeli_phone("050-1234567") == "+972501234567"


def test_phone_normalization_international():
    assert rpm.normalize_israeli_phone("+972 50 123 4567") == "+972501234567"


def test_invalid_phone():
    with pytest.raises(rpm.ValidationError):
        rpm.normalize_israeli_phone("03-1234567")


def test_email_normalization():
    assert rpm.normalize_email("  USER@Example.CO.IL ") == "user@example.co.il"


def test_invalid_email():
    with pytest.raises(rpm.ValidationError):
        rpm.normalize_email("not-an-email")


def test_israeli_id_validation_known_valid():
    assert rpm.validate_israeli_id("000000018") is True


def test_dd_mm_yyyy_parser():
    assert rpm.parse_dd_mm_yyyy("31-03-2026").isoformat() == "2026-03-31"


def test_dd_mm_yyyy_parser_rejects_bad_format():
    with pytest.raises(rpm.ValidationError):
        rpm.parse_dd_mm_yyyy("2026-03-31")


def test_create_program_reward_money():
    m = manager_with_program()
    assert str(m.programs["p1"].reward_amount_ils) == "50.00"


def test_add_customer_audit_log():
    m = manager_with_program()
    assert any(entry.action == "add_customer" for entry in m.audit_log)


def test_generate_referral_link():
    m = manager_with_program()
    link = m.generate_referral_link("p1", "c1", "https://example.co.il/ref")
    assert "ref=R-" in link and "program=p1" in link


def test_register_referral_success():
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    assert event.status.value == "registered"


def test_register_referral_duplicate():
    m = manager_with_program()
    m.register_referral("p1", "c1", "c2", "manual")
    with pytest.raises(rpm.DuplicateReferralError):
        m.register_referral("p1", "c1", "c2", "manual")


def test_self_referral_blocked():
    m = manager_with_program()
    with pytest.raises(rpm.ValidationError):
        m.register_referral("p1", "c1", "c1", "manual")


def test_same_phone_goes_to_fraud_review():
    m = rpm.ReferralProgramManager()
    m.create_program("p1", "Test", "credit", 50, "paid", cooldown_days=0)
    m.add_customer("c1", "Dana", "dana@example.co.il", "050-1234567")
    m.add_customer("c2", "Noa", "noa@example.co.il", "+972501234567")
    event = m.register_referral("p1", "c1", "c2", "manual")
    assert event.status.value == "fraud_review"
    assert event.fraud_score == 100


def test_qualify_requires_evidence():
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    with pytest.raises(rpm.ValidationError):
        m.qualify_referral(event.event_id)


def test_qualify_minimum_order():
    m = manager_with_program(minimum_order=199)
    event = m.register_referral("p1", "c1", "c2", "manual")
    with pytest.raises(rpm.ValidationError):
        m.qualify_referral(event.event_id, evidence={"invoice": "1"}, order_amount_ils=100)


def test_approve_reward_success():
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"}, order_amount_ils=200)
    reward = m.approve_reward(event.event_id, actor="owner", tax_treatment="customer_credit")
    assert reward.status.value == "approved"
    assert reward.tax_treatment == "customer_credit"


def test_approve_respects_cooldown():
    m = manager_with_program(cooldown_days=14)
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    with pytest.raises(rpm.ValidationError):
        m.approve_reward(event.event_id, actor="owner")


def test_approve_force_bypasses_cooldown():
    m = manager_with_program(cooldown_days=14)
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    reward = m.approve_reward(event.event_id, actor="owner", force=True)
    assert reward.status.value == "approved"


def test_reward_cap():
    m = rpm.ReferralProgramManager()
    m.create_program("p1", "Cap", "credit", 10, "paid", cooldown_days=0, max_rewards_per_customer=1)
    m.add_customer("c1", "Dana", "dana@example.co.il", "050-1234567")
    m.add_customer("c2", "Noa", "noa@example.co.il", "052-7654321")
    m.add_customer("c3", "Ron", "ron@example.co.il", "053-7654321")
    e1 = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(e1.event_id, evidence={"invoice": "1"})
    m.approve_reward(e1.event_id, actor="owner")
    e2 = m.register_referral("p1", "c1", "c3", "manual")
    m.qualify_referral(e2.event_id, evidence={"invoice": "2"})
    with pytest.raises(rpm.ValidationError):
        m.approve_reward(e2.event_id, actor="owner")


def test_gateway_refund_payload():
    adapter = rpm.GatewayAdapter("payplus")
    payload = adapter.build_refund_request("TX1", 50, "referral_reward", "idem-1")
    assert payload["currency"] == "ILS"
    assert payload["operation"] == "refund"


def test_gateway_credit_payload():
    adapter = rpm.GatewayAdapter("cardcom")
    payload = adapter.build_credit_request("c1", "25.5", "30-09-2026")
    assert payload["amount"] == "25.50"


def test_gateway_parse_webhook():
    adapter = rpm.GatewayAdapter("tranzila")
    mapped = adapter.parse_webhook({"status": "approved", "metadata": {"reward_id": "r1"}, "transaction_id": "T1"})
    assert mapped["status"] == "paid"
    assert mapped["reward_id"] == "r1"


def test_webhook_signature():
    raw = b'{"reward_id":"r1"}'
    sig = "sha256=" + hmac.new(b"secret", raw, hashlib.sha256).hexdigest()
    assert rpm.verify_webhook_signature(raw, sig, "secret")


def test_sync_gateway_client_submit_default():
    gateway_client = rpm.PaymentGatewayClient(rpm.GatewayAdapter("manual"))
    response = gateway_client.submit({"x": 1})
    assert response["status"] == "submitted"


@pytest.mark.asyncio
async def test_async_gateway_client_submit_default():
    gateway_client = rpm.PaymentGatewayClient(rpm.GatewayAdapter("manual"))
    response = await gateway_client.submit_async({"x": 1})
    assert response["status"] == "submitted"


def test_apply_gateway_response_marks_paid():
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    reward = m.approve_reward(event.event_id, actor="owner")
    updated = m.apply_gateway_response(reward.reward_id, {"provider": "manual", "status": "approved", "gateway_reference": "GW1"})
    assert updated.status.value == "paid"
    assert updated.gateway_reference == "GW1"


def test_export_rewards_csv(tmp_path):
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    m.approve_reward(event.event_id, actor="owner")
    path = tmp_path / "rewards.csv"
    m.export_rewards_csv(path, status="approved")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["amount_ils"] == "50.00"


def test_json_round_trip(tmp_path):
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    m.approve_reward(event.event_id, actor="owner")
    path = tmp_path / "state.json"
    m.save_json(path)
    loaded = rpm.ReferralProgramManager.load_json(path)
    assert len(loaded.rewards) == 1
    assert loaded.customers["c1"].phone == "+972501234567"


def test_reverse_reward():
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    reward = m.approve_reward(event.event_id, actor="owner")
    reversed_reward = m.reverse_reward(reward.reward_id, "refund")
    assert reversed_reward.status.value == "reversed"


def test_build_gateway_payload_for_credit():
    m = manager_with_program()
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    reward = m.approve_reward(event.event_id, actor="owner")
    payload = m.build_reward_gateway_payload(reward.reward_id, "payplus")
    assert payload["operation"] == "credit"
    assert payload["metadata"]["reward_id"] == reward.reward_id


def test_refund_reward_requires_original_transaction():
    m = manager_with_program(reward_type="refund")
    event = m.register_referral("p1", "c1", "c2", "manual")
    m.qualify_referral(event.event_id, evidence={"invoice": "INV-1"})
    reward = m.approve_reward(event.event_id, actor="owner")
    with pytest.raises(rpm.ValidationError):
        m.build_reward_gateway_payload(reward.reward_id, "payplus")


def test_demo_manager():
    m = rpm.create_demo_manager()
    assert len(m.rewards) == 1


def test_cli_help():
    cli = Path(__file__).with_name("referral-program-manager-cli.py")
    result = subprocess.run([sys.executable, str(cli), "--help"], cwd=Path(__file__).parents[1], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Manage referral programs" in result.stdout


def test_cli_create_program_json(tmp_path):
    cli = Path(__file__).with_name("referral-program-manager-cli.py")
    state = tmp_path / "state.json"
    subprocess.run([sys.executable, str(cli), "init-state", "--state", str(state)], cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True)
    result = subprocess.run(
        [
            sys.executable,
            str(cli),
            "create-program",
            "--state",
            str(state),
            "--program-id",
            "p-cli",
            "--name",
            "CLI",
            "--reward-amount",
            "10",
            "--qualifying-action",
            "paid",
        ],
        cwd=Path(__file__).parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["program_id"] == "p-cli"


def test_example_json_output():
    example = Path(__file__).parent / "examples" / "salon_referral_program.py"
    result = subprocess.run([sys.executable, str(example), "--env", "sandbox"], cwd=Path(__file__).parents[1], capture_output=True, text=True)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["environment"] == "sandbox"
    assert payload["scenario"] == "salon_credit"


def test_gateway_legacy_aliases_normalize():
    assert rpm.GatewayAdapter("meshulam").provider == "grow"
    assert rpm.GatewayAdapter("yaadpay").provider == "yabandpay"
