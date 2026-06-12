"""Installable local client for Israeli emergency contact and first-aid profiles.

The package stores data locally, validates profiles, renders safe summaries,
and returns dispatch-first first-aid prompts. It does not replace emergency
dispatch, certified training, or current official medical guidance.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime
import json
from pathlib import Path
import re
import sys
import uuid
from typing import Any, Dict, List, Mapping, Optional, Sequence


SUPPORTED_SHORT_CODES = {"100", "101", "102", "103", "104", "106", "107", "1221"}
DEFAULT_EMERGENCY_SERVICES: Dict[str, str] = {
    "medical": "101",
    "police": "100",
    "fire_rescue": "102",
    "electric": "103",
    "home_front": "104",
    "municipal": "106",
    "united_hatzalah": "1221",
    "mda_sms_whatsapp": "052-7000-101",
}
PHONE_RE = re.compile(r"^(?:\+972|0)(?:[23489]\d{7}|5\d{8}|7\d{8})$")
DATE_RE = re.compile(r"^\d{2}[-/]\d{2}[-/]\d{4}$")
ID_LIKE_RE = re.compile(r"(?<!\d)\d{9}(?!\d)")


class EmergencyContact:
    """Emergency contact with escalation priority."""

    def __init__(
        self,
        name: str,
        phone: str,
        priority: int,
        role: str = "",
        relationship: str = "",
        can_receive_medical_info: bool = False,
    ) -> None:
        self.name = str(name).strip()
        self.phone = str(phone).strip()
        self.priority = int(priority)
        self.role = str(role).strip()
        self.relationship = str(relationship).strip()
        self.can_receive_medical_info = bool(can_receive_medical_info)

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "phone": self.phone,
            "priority": self.priority,
            "role": self.role,
            "relationship": self.relationship,
            "can_receive_medical_info": self.can_receive_medical_info,
        }


class SiteInfo:
    """Site and access details used by dispatchers and responders."""

    def __init__(
        self,
        address_line: str,
        locality: str,
        access_notes: str = "",
        aed_location: str = "",
        first_aid_kit_location: str = "",
    ) -> None:
        self.address_line = str(address_line).strip()
        self.locality = str(locality).strip()
        self.access_notes = str(access_notes).strip()
        self.aed_location = str(aed_location).strip()
        self.first_aid_kit_location = str(first_aid_kit_location).strip()

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "address_line": self.address_line,
            "locality": self.locality,
            "access_notes": self.access_notes,
            "aed_location": self.aed_location,
            "first_aid_kit_location": self.first_aid_kit_location,
        }


class MedicalNotes:
    """Emergency-relevant medical context."""

    def __init__(
        self,
        known_allergies: Optional[Sequence[str]] = None,
        regular_medications: Optional[Sequence[str]] = None,
        conditions_relevant_to_emergency: Optional[Sequence[str]] = None,
        mobility_needs: Optional[Sequence[str]] = None,
    ) -> None:
        self.known_allergies = list(known_allergies or [])
        self.regular_medications = list(regular_medications or [])
        self.conditions_relevant_to_emergency = list(conditions_relevant_to_emergency or [])
        self.mobility_needs = list(mobility_needs or [])

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "known_allergies": list(self.known_allergies),
            "regular_medications": list(self.regular_medications),
            "conditions_relevant_to_emergency": list(self.conditions_relevant_to_emergency),
            "mobility_needs": list(self.mobility_needs),
        }


class EmergencyProfile:
    """Complete local emergency profile."""

    def __init__(
        self,
        profile_name: str,
        last_reviewed: str,
        site: SiteInfo,
        contacts: Sequence[EmergencyContact],
        emergency_services: Optional[Mapping[str, str]] = None,
        medical_notes: Optional[MedicalNotes] = None,
        consent: Optional[Mapping[str, Any]] = None,
        profile_id: Optional[str] = None,
        environment: str = "sandbox",
    ) -> None:
        services = dict(DEFAULT_EMERGENCY_SERVICES)
        services.update({str(key): str(value) for key, value in dict(emergency_services or {}).items()})
        self.profile_id = profile_id or str(uuid.uuid4())
        self.profile_name = str(profile_name).strip()
        self.last_reviewed = str(last_reviewed).strip()
        self.site = site
        self.contacts = list(contacts)
        self.emergency_services = services
        self.medical_notes = medical_notes or MedicalNotes()
        self.consent = dict(consent or {})
        self.environment = environment

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "id": self.profile_id,
            "environment": self.environment,
            "profile_name": self.profile_name,
            "last_reviewed": self.last_reviewed,
            "site": self.site.to_mapping(),
            "emergency_services": dict(self.emergency_services),
            "contacts": [item.to_mapping() for item in self.contacts],
            "medical_notes": self.medical_notes.to_mapping(),
            "consent": dict(self.consent),
        }


class ValidationResult:
    """Validation response for profile checks."""

    def __init__(self, ok: bool, errors: Sequence[str], warnings: Sequence[str], contacts_count: int) -> None:
        self.ok = bool(ok)
        self.errors = list(errors)
        self.warnings = list(warnings)
        self.contacts_count = int(contacts_count)

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "contacts_count": self.contacts_count,
        }


class TriageResult:
    """First-aid decision support response."""

    def __init__(
        self,
        scenario: str,
        emergency_call: str,
        priority: str,
        actions: Sequence[str],
        do_not: Sequence[str],
    ) -> None:
        self.scenario = scenario
        self.emergency_call = emergency_call
        self.priority = priority
        self.actions = list(actions)
        self.do_not = list(do_not)

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "emergency_call": self.emergency_call,
            "priority": self.priority,
            "actions": list(self.actions),
            "do_not": list(self.do_not),
        }


def contact_from_mapping(data: Mapping[str, Any]) -> EmergencyContact:
    return EmergencyContact(
        name=str(data.get("name", "")).strip(),
        phone=str(data.get("phone", "")).strip(),
        priority=int(data.get("priority", 99)),
        role=str(data.get("role", "")).strip(),
        relationship=str(data.get("relationship", "")).strip(),
        can_receive_medical_info=bool(data.get("can_receive_medical_info", False)),
    )


def site_from_mapping(data: Mapping[str, Any]) -> SiteInfo:
    return SiteInfo(
        address_line=str(data.get("address_line", "")).strip(),
        locality=str(data.get("locality", "")).strip(),
        access_notes=str(data.get("access_notes", "")).strip(),
        aed_location=str(data.get("aed_location", "")).strip(),
        first_aid_kit_location=str(data.get("first_aid_kit_location", "")).strip(),
    )


def medical_notes_from_mapping(data: Optional[Mapping[str, Any]]) -> MedicalNotes:
    data = data or {}
    return MedicalNotes(
        known_allergies=list(data.get("known_allergies", []) or []),
        regular_medications=list(data.get("regular_medications", []) or []),
        conditions_relevant_to_emergency=list(data.get("conditions_relevant_to_emergency", []) or []),
        mobility_needs=list(data.get("mobility_needs", []) or []),
    )


def profile_from_mapping(data: Mapping[str, Any]) -> EmergencyProfile:
    services = dict(DEFAULT_EMERGENCY_SERVICES)
    services.update({str(key): str(value) for key, value in dict(data.get("emergency_services", {}) or {}).items()})
    return EmergencyProfile(
        profile_id=str(data.get("id", "") or data.get("profile_id", "") or uuid.uuid4()),
        environment=str(data.get("environment", "sandbox")),
        profile_name=str(data.get("profile_name", "")).strip(),
        last_reviewed=str(data.get("last_reviewed", "")).strip(),
        site=site_from_mapping(data.get("site", {}) or {}),
        emergency_services=services,
        contacts=[contact_from_mapping(item) for item in (data.get("contacts", []) or [])],
        medical_notes=medical_notes_from_mapping(data.get("medical_notes", {}) or {}),
        consent=dict(data.get("consent", {}) or {}),
    )


def parse_local_date(value: str) -> date:
    """Parse DD-MM-YYYY or DD/MM/YYYY."""

    if not DATE_RE.match(value):
        raise ValueError("date must use DD-MM-YYYY or DD/MM/YYYY")
    separator = "/" if "/" in value else "-"
    return datetime.strptime(value, f"%d{separator}%m{separator}%Y").date()


def normalize_israeli_phone(phone: str) -> str:
    """Return a normalized Israeli phone number or supported emergency short code."""

    cleaned = re.sub(r"[\s().-]", "", str(phone).strip())
    if cleaned in SUPPORTED_SHORT_CODES:
        return cleaned
    if cleaned.startswith("00972"):
        cleaned = "+972" + cleaned[5:]
    if cleaned.startswith("972"):
        cleaned = "+" + cleaned
    if cleaned.startswith("+972"):
        local_candidate = "0" + cleaned[4:]
        if PHONE_RE.match(local_candidate):
            return cleaned
    if PHONE_RE.match(cleaned):
        return "+972" + cleaned[1:] if cleaned.startswith("0") else cleaned
    raise ValueError("phone must be an Israeli phone number or supported emergency short code")


def is_supported_phone(phone: str) -> bool:
    try:
        normalize_israeli_phone(phone)
        return True
    except ValueError:
        return False


def contains_id_like_value(value: Any) -> bool:
    return bool(ID_LIKE_RE.search(json.dumps(value, ensure_ascii=False, sort_keys=True)))


def days_since_review(last_reviewed: str, today: Optional[date] = None) -> Optional[int]:
    try:
        reviewed = parse_local_date(last_reviewed)
    except ValueError:
        return None
    today = today or date.today()
    return (today - reviewed).days


def validate_profile(
    profile: EmergencyProfile | Mapping[str, Any],
    strict_privacy: bool = False,
    today: Optional[date] = None,
) -> ValidationResult:
    original_profile_value: Any = profile
    if not isinstance(profile, EmergencyProfile):
        profile = profile_from_mapping(profile)

    errors: List[str] = []
    warnings: List[str] = []

    if len(profile.profile_name) < 2:
        errors.append("profile_name must contain at least 2 characters")
    if not DATE_RE.match(profile.last_reviewed):
        errors.append("last_reviewed must use DD-MM-YYYY or DD/MM/YYYY")
    else:
        age = days_since_review(profile.last_reviewed, today=today)
        if age is not None and age > 90:
            warnings.append("Review date is more than 90 days old")
        if age is not None and age < -1:
            warnings.append("Review date is in the future")

    if len(profile.site.address_line) < 3:
        errors.append("site.address_line is required")
    if len(profile.site.locality) < 2:
        errors.append("site.locality is required")
    if not profile.site.access_notes:
        warnings.append("Access notes are missing")
    if not profile.site.aed_location:
        warnings.append("AED location is missing")
    if not profile.site.first_aid_kit_location:
        warnings.append("First-aid kit location is missing")

    if not profile.contacts:
        errors.append("at least one emergency contact is required")

    priorities: set[int] = set()
    for index, contact in enumerate(profile.contacts):
        prefix = f"contacts[{index}]"
        if len(contact.name) < 2:
            errors.append(f"{prefix}.name must contain at least 2 characters")
        if not is_supported_phone(contact.phone):
            errors.append(f"{prefix}.phone must be an Israeli phone number or supported emergency short code")
        if not 1 <= contact.priority <= 99:
            errors.append(f"{prefix}.priority must be between 1 and 99")
        if contact.priority in priorities:
            errors.append("contact priorities must be unique")
        priorities.add(contact.priority)

    for key in ("medical", "police", "fire_rescue"):
        if not profile.emergency_services.get(key):
            warnings.append(f"emergency service {key} is missing")
    if profile.emergency_services.get("medical") != "101":
        warnings.append("medical emergency service should normally be 101 in Israel")

    privacy_scan_value = original_profile_value if strict_privacy else profile.to_mapping()
    if strict_privacy and contains_id_like_value(privacy_scan_value):
        errors.append("possible Israeli ID number detected")

    return ValidationResult(not errors, errors, warnings, len(profile.contacts))


def triage_first_aid(
    scenario: str,
    age_group: str = "adult",
    conscious: Optional[bool] = None,
    breathing: Optional[bool] = None,
    severe_bleeding: bool = False,
    chest_pain: bool = False,
    stroke_signs: bool = False,
) -> TriageResult:
    normalized = scenario.strip().lower().replace("-", "_").replace(" ", "_")
    actions: List[str] = []
    do_not: List[str] = []
    priority = "yellow"

    if conscious is False and breathing is False:
        return TriageResult(
            normalized,
            "101",
            "red",
            [
                "Call 101 now",
                "Put phone on speaker",
                "Send someone for an AED",
                "Start chest compressions in the center of the chest",
                "Attach AED and follow prompts",
            ],
            [
                "Do not delay CPR to search for documents",
                "Do not check pulse unless trained",
            ],
        )

    if normalized in {"cpr", "cardiac_arrest", "unresponsive"}:
        priority = "red"
        actions.extend(["Call 101 now", "Check breathing", "Bring AED", "Follow dispatcher instructions"])
        do_not.extend(["Do not delay call for forms", "Do not leave the person alone"])
    elif normalized in {"severe_bleeding", "bleeding"} or severe_bleeding:
        priority = "red"
        actions.extend(["Call 101 now", "Apply firm direct pressure", "Use pressure bandage if available", "Keep warm"])
        do_not.extend(["Do not remove soaked dressings", "Do not use a tourniquet unless trained or instructed"])
    elif normalized in {"choking", "airway_obstruction"}:
        priority = "red"
        actions.append("Call 101 now")
        if age_group == "infant":
            actions.extend(["Give 5 back blows and 5 chest thrusts", "Support the head lower than the body"])
            do_not.append("Do not use abdominal thrusts on an infant")
        else:
            actions.extend(["Encourage effective coughing", "Use abdominal thrusts if trained and airway is blocked", "Start CPR if collapse occurs"])
        do_not.append("Do not perform blind finger sweeps")
    elif normalized in {"chest_pain", "heart_attack"} or chest_pain:
        priority = "red"
        actions.extend(["Call 101 now", "Keep the person resting", "Prepare medication and allergy information"])
        do_not.extend(["Do not let the person drive", "Do not give aspirin unless instructed"])
    elif normalized in {"stroke", "fast"} or stroke_signs:
        priority = "red"
        actions.extend(["Call 101 now", "Record exact last-known-well time", "Use face, arm, speech, time checks"])
        do_not.extend(["Do not give food, drink, or medication", "Do not wait for symptoms to pass"])
    elif normalized in {"anaphylaxis", "allergic_reaction"}:
        priority = "red"
        actions.extend(["Call 101 now", "Help use the prescribed adrenaline auto-injector if available and indicated", "Monitor breathing"])
        do_not.extend(["Do not make the person walk", "Do not delay the call"])
    elif normalized in {"burn", "burns"}:
        priority = "orange"
        actions.extend(["Cool under cool running water for about 20 minutes", "Remove tight items near the burn", "Cover with clean non-stick dressing", "Call 101 for serious burns"])
        do_not.extend(["Do not use ice, butter, oil, or toothpaste", "Do not burst blisters"])
    elif normalized in {"seizure", "convulsion"}:
        priority = "orange"
        actions.extend(["Protect from injury", "Time the seizure", "Call 101 for seizure over 5 minutes or red flags", "Place in recovery position after convulsions stop if breathing normally"])
        do_not.extend(["Do not restrain", "Do not put anything in the mouth"])
    elif normalized in {"heat_illness", "heatstroke", "heat_stroke"}:
        priority = "red"
        actions.extend(["Call 101 for confusion, collapse, seizure, or worsening symptoms", "Move to shade or air conditioning", "Cool with water and air movement"])
        do_not.append("Do not give water if not fully awake")
    elif normalized in {"poisoning", "chemical_exposure"}:
        priority = "orange"
        actions.extend(["Call 101 for severe symptoms or dangerous exposure", "Rinse chemical exposure with water", "Keep the container or label for responders"])
        do_not.append("Do not induce vomiting unless instructed")
    elif normalized in {"electric_shock", "electrocution"}:
        priority = "red"
        actions.extend(["Do not touch until power is off", "Call 103 for electric infrastructure hazard", "Call 101 for injury", "Start CPR only when safe"])
        do_not.append("Do not enter an unsafe electrical area")
    elif normalized in {"minor_cut", "minor_injury"}:
        priority = "green"
        actions.extend(["Clean the wound", "Apply dressing", "Monitor for worsening", "Document workplace incidents"])
        do_not.append("Do not ignore infection signs")
    else:
        actions.extend(["Check scene safety", "Call 101 if any red flag appears", "Use trained first aid only", "Document after urgent phase"])
        do_not.append("Do not delay emergency calls to complete forms")

    return TriageResult(normalized, "101", priority, actions, do_not)


def make_starter_profile(
    profile_name: str,
    address: str,
    locality: str,
    contact_name: str,
    contact_phone: str,
    environment: str = "sandbox",
) -> EmergencyProfile:
    return EmergencyProfile(
        profile_name=profile_name,
        last_reviewed=date.today().strftime("%d-%m-%Y"),
        environment=environment,
        site=SiteInfo(address, locality),
        contacts=[EmergencyContact(contact_name, contact_phone, 1, role="Primary contact")],
    )


class EmergencyInfoClient:
    """Synchronous local client."""

    def load_profile(self, path: str | Path) -> EmergencyProfile:
        with Path(path).open("r", encoding="utf-8") as handle:
            return profile_from_mapping(json.load(handle))

    def save_profile(self, profile: EmergencyProfile, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(profile.to_mapping(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    def validate_profile(
        self,
        profile: EmergencyProfile | Mapping[str, Any],
        strict_privacy: bool = False,
        today: Optional[date] = None,
    ) -> ValidationResult:
        return validate_profile(profile, strict_privacy=strict_privacy, today=today)

    def normalize_phone(self, phone: str) -> str:
        return normalize_israeli_phone(phone)

    def sorted_contacts(self, profile: EmergencyProfile) -> List[EmergencyContact]:
        return sorted(profile.contacts, key=lambda item: item.priority)

    def render_wallet_card(self, profile: EmergencyProfile) -> str:
        contacts = self.sorted_contacts(profile)
        primary = contacts[0] if contacts else EmergencyContact("", "", 99)
        allergies = ", ".join(profile.medical_notes.known_allergies) or "None recorded"
        medications = ", ".join(profile.medical_notes.regular_medications) or "None recorded"
        return "\n".join(
            [
                "# Emergency wallet card",
                "",
                f"Profile ID: {profile.profile_id}",
                f"Profile: {profile.profile_name}",
                f"Address: {profile.site.address_line}, {profile.site.locality}",
                "Medical emergency: 101",
                "Police: 100",
                "Fire and rescue: 102",
                f"Primary contact: {primary.name} — {primary.role or primary.relationship} — {primary.phone}",
                f"Allergies: {allergies}",
                f"Medication notes: {medications}",
                f"Access notes: {profile.site.access_notes or 'None recorded'}",
                f"Review date: {profile.last_reviewed}",
                "",
            ]
        )

    def redact_profile(self, profile: EmergencyProfile | Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(profile, EmergencyProfile):
            profile = profile_from_mapping(profile)
        contacts = [
            {
                "name": contact.name,
                "role": contact.role,
                "phone": contact.phone,
                "priority": contact.priority,
            }
            for contact in self.sorted_contacts(profile)
        ]
        return {
            "id": profile.profile_id,
            "environment": profile.environment,
            "profile_name": profile.profile_name,
            "last_reviewed": profile.last_reviewed,
            "site": {
                "address_line": profile.site.address_line,
                "locality": profile.site.locality,
                "aed_location": profile.site.aed_location,
                "first_aid_kit_location": profile.site.first_aid_kit_location,
            },
            "emergency_services": dict(profile.emergency_services),
            "contacts": contacts,
        }

    def triage(self, scenario: str, **kwargs: Any) -> TriageResult:
        return triage_first_aid(scenario, **kwargs)

    def create_profile(
        self,
        profile_name: str,
        address: str,
        locality: str,
        contact_name: str,
        contact_phone: str,
        store_dir: str | Path,
        environment: str = "sandbox",
    ) -> Dict[str, Any]:
        profile = make_starter_profile(profile_name, address, locality, contact_name, contact_phone, environment)
        store = Path(store_dir)
        store.mkdir(parents=True, exist_ok=True)
        path = store / f"{profile.profile_id}.json"
        self.save_profile(profile, path)
        return {"ok": True, "id": profile.profile_id, "path": str(path), "environment": environment}

    def load_profile_by_id(self, profile_id: str, store_dir: str | Path) -> EmergencyProfile:
        return self.load_profile(Path(store_dir) / f"{profile_id}.json")


class AsyncEmergencyInfoClient:
    """Asynchronous local client wrapper."""

    def __init__(self, sync_client: Optional[EmergencyInfoClient] = None) -> None:
        self._sync = sync_client or EmergencyInfoClient()

    async def load_profile(self, path: str | Path) -> EmergencyProfile:
        return await asyncio.to_thread(self._sync.load_profile, path)

    async def save_profile(self, profile: EmergencyProfile, path: str | Path) -> None:
        await asyncio.to_thread(self._sync.save_profile, profile, path)

    async def validate_profile(
        self,
        profile: EmergencyProfile | Mapping[str, Any],
        strict_privacy: bool = False,
        today: Optional[date] = None,
    ) -> ValidationResult:
        return await asyncio.to_thread(self._sync.validate_profile, profile, strict_privacy, today)

    async def render_wallet_card(self, profile: EmergencyProfile) -> str:
        return await asyncio.to_thread(self._sync.render_wallet_card, profile)

    async def redact_profile(self, profile: EmergencyProfile | Mapping[str, Any]) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync.redact_profile, profile)

    async def triage(self, scenario: str, **kwargs: Any) -> TriageResult:
        return await asyncio.to_thread(self._sync.triage, scenario, **kwargs)


def json_print(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def yes_no_to_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"yes", "true", "1", "y"}:
        return True
    if normalized in {"no", "false", "0", "n"}:
        return False
    raise argparse.ArgumentTypeError("expected yes or no")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emergency contact and first-aid local helper")
    sub = parser.add_subparsers(dest="command", required=True)

    create_cmd = sub.add_parser("create-profile", help="Create a profile and return its id")
    create_cmd.add_argument("--profile-name", required=True)
    create_cmd.add_argument("--address", required=True)
    create_cmd.add_argument("--locality", required=True)
    create_cmd.add_argument("--contact-name", required=True)
    create_cmd.add_argument("--contact-phone", required=True)
    create_cmd.add_argument("--store-dir", default=".ecfa-sandbox")
    create_cmd.add_argument("--env", default="sandbox", choices=["sandbox", "production"])

    validate_cmd = sub.add_parser("validate", help="Validate an emergency profile")
    validate_cmd.add_argument("profile", nargs="?")
    validate_cmd.add_argument("--profile-id")
    validate_cmd.add_argument("--store-dir", default=".ecfa-sandbox")
    validate_cmd.add_argument("--strict", action="store_true")
    validate_cmd.add_argument("--env", default="sandbox", choices=["sandbox", "production"])

    wallet_cmd = sub.add_parser("wallet-card", help="Render a wallet card")
    wallet_cmd.add_argument("profile", nargs="?")
    wallet_cmd.add_argument("--profile-id")
    wallet_cmd.add_argument("--store-dir", default=".ecfa-sandbox")
    wallet_cmd.add_argument("--env", default="sandbox", choices=["sandbox", "production"])

    redact_cmd = sub.add_parser("redact", help="Print redacted public profile")
    redact_cmd.add_argument("profile", nargs="?")
    redact_cmd.add_argument("--profile-id")
    redact_cmd.add_argument("--store-dir", default=".ecfa-sandbox")
    redact_cmd.add_argument("--env", default="sandbox", choices=["sandbox", "production"])

    triage_cmd = sub.add_parser("triage", help="Return first-aid triage prompt")
    triage_cmd.add_argument("--scenario", required=True)
    triage_cmd.add_argument("--age-group", default="adult", choices=["adult", "child", "infant"])
    triage_cmd.add_argument("--conscious", type=yes_no_to_bool)
    triage_cmd.add_argument("--breathing", type=yes_no_to_bool)
    triage_cmd.add_argument("--severe-bleeding", action="store_true")
    triage_cmd.add_argument("--chest-pain", action="store_true")
    triage_cmd.add_argument("--stroke-signs", action="store_true")
    triage_cmd.add_argument("--env", default="sandbox", choices=["sandbox", "production"])

    numbers_cmd = sub.add_parser("numbers", help="Show Israeli emergency numbers")
    numbers_cmd.add_argument("--json", action="store_true")
    numbers_cmd.add_argument("--env", default="sandbox", choices=["sandbox", "production"])

    return parser


def load_from_path_or_id(client: EmergencyInfoClient, profile_path: Optional[str], profile_id: Optional[str], store_dir: str) -> EmergencyProfile:
    if profile_id:
        return client.load_profile_by_id(profile_id, store_dir)
    if profile_path:
        return client.load_profile(profile_path)
    raise ValueError("profile path or profile id is required")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    client = EmergencyInfoClient()
    try:
        if args.command == "create-profile":
            json_print(
                client.create_profile(
                    args.profile_name,
                    args.address,
                    args.locality,
                    args.contact_name,
                    args.contact_phone,
                    args.store_dir,
                    args.env,
                )
            )
            return 0
        if args.command == "validate":
            profile = load_from_path_or_id(client, args.profile, args.profile_id, args.store_dir)
            result = client.validate_profile(profile, strict_privacy=args.strict)
            json_print(result.to_mapping())
            return 0 if result.ok else 1
        if args.command == "wallet-card":
            profile = load_from_path_or_id(client, args.profile, args.profile_id, args.store_dir)
            print(client.render_wallet_card(profile), end="")
            return 0
        if args.command == "redact":
            profile = load_from_path_or_id(client, args.profile, args.profile_id, args.store_dir)
            json_print(client.redact_profile(profile))
            return 0
        if args.command == "triage":
            json_print(
                client.triage(
                    args.scenario,
                    age_group=args.age_group,
                    conscious=args.conscious,
                    breathing=args.breathing,
                    severe_bleeding=args.severe_bleeding,
                    chest_pain=args.chest_pain,
                    stroke_signs=args.stroke_signs,
                ).to_mapping()
            )
            return 0
        if args.command == "numbers":
            if args.json:
                json_print(DEFAULT_EMERGENCY_SERVICES)
            else:
                for key, value in DEFAULT_EMERGENCY_SERVICES.items():
                    print(f"{key}: {value}")
            return 0
    except FileNotFoundError as exc:
        print(f"File not found: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
