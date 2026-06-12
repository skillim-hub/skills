import asyncio
from datetime import date, time

import pytest

from recruitment_assistant import (
    AsyncRecruitmentAssistantClient,
    Candidate,
    RecruitmentAssistantClient,
    RecruitmentAssistantError,
    RoleProfile,
    detect_languages,
    extract_email,
    extract_phone,
    extract_skills,
    extract_years_experience,
    format_israeli_date,
    normalize_role_family,
    normalize_seniority,
    normalize_terms,
    validate_job_ad,
)


def client():
    return RecruitmentAssistantClient(env="sandbox")


def test_normalize_hebrew_accounting_role():
    assert normalize_role_family("מנהלת חשבונות עם חשבשבת") == "accounting"


def test_normalize_english_software_role():
    assert normalize_role_family("Senior Python Developer") == "software"


def test_normalize_customer_service_role():
    assert normalize_role_family("נציג שירות לקוחות") == "customer_service"


def test_normalize_marketing_role():
    assert normalize_role_family("PPC and SEO specialist") == "marketing"


def test_normalize_unknown_role():
    assert normalize_role_family("general helper") == "unknown"


def test_normalize_seniority_from_hebrew_lead():
    assert normalize_seniority("ראש צוות תפעול") == "lead"


def test_normalize_seniority_from_years():
    assert normalize_seniority("8 years experience") == "senior"


def test_extract_email():
    assert extract_email("Contact dana@example.co.il now") == "dana@example.co.il"


def test_extract_phone():
    assert extract_phone("Phone 052-1234567") == "052-1234567"


def test_detect_languages_mixed():
    assert detect_languages("עברית and English") == ["hebrew", "english"]


def test_extract_years_hebrew():
    assert extract_years_experience("5 שנות ניסיון") == 5


def test_extract_years_english():
    assert extract_years_experience("4 years experience") == 4


def test_extract_skills_with_hebrew_alias():
    found = extract_skills("עבדתי עם חשבשבת ואקסל")
    assert "חשבשבת" in found
    assert "אקסל" in found


def test_normalize_terms_deduplicates():
    assert normalize_terms(["SQL", " sql ", "Python"]) == ["sql", "python"]


def test_create_candidate_extracts_contact():
    response = client().create_candidate(Candidate(name="Dana", resume_text="dana@example.com 052-1234567 Python"))
    assert response["id"]
    assert response["candidate"]["email"] == "dana@example.com"
    assert response["candidate"]["phone"] == "052-1234567"


def test_get_candidate_after_create():
    c = client()
    response = c.create_candidate(Candidate(name="Dana", resume_text="dana@example.com Python"))
    candidate = c.get_candidate(response["id"])
    assert candidate.name == "Dana"


def test_get_unknown_candidate_raises():
    with pytest.raises(RecruitmentAssistantError):
        client().get_candidate("missing")


def test_empty_resume_raises():
    with pytest.raises(RecruitmentAssistantError):
        client().create_candidate(Candidate(name="Dana", resume_text=""))


def test_screen_hebrew_bookkeeper_advances():
    c = client()
    role = RoleProfile(title="מנהלת חשבונות", required_skills=["חשבשבת", "אקסל"], seniority="mid")
    candidate = Candidate(name="Noa", resume_text="noa@example.co.il 054-1234567 חשבשבת אקסל 5 שנות ניסיון")
    result = c.screen_resume(candidate, role)
    assert result.recommendation == "advance"
    assert result.role_family == "accounting"
    assert not result.missing_required


def test_screen_missing_required_declines_or_reviews():
    c = client()
    role = RoleProfile(title="Python Developer", required_skills=["python", "sql"], seniority="mid")
    candidate = Candidate(name="Omer", resume_text="omer@example.com Python 1 years experience")
    result = c.screen_resume(candidate, role)
    assert "sql" in result.missing_required
    assert result.recommendation in {"review", "decline"}


def test_rank_candidates_orders_by_score():
    c = client()
    role = RoleProfile(title="Python Developer", required_skills=["python", "sql"], preferred_skills=["react"], seniority="mid")
    candidates = [
        Candidate(name="B", resume_text="b@example.com Python 1 years experience"),
        Candidate(name="A", resume_text="a@example.com Python SQL React 4 years experience"),
    ]
    ranked = c.rank_candidates(candidates, role)
    assert ranked[0].candidate_name == "A"


def test_shortlist_filters_minimum_score():
    c = client()
    role = RoleProfile(title="Python Developer", required_skills=["python", "sql"], seniority="mid")
    candidates = [
        Candidate(name="Strong", resume_text="strong@example.com Python SQL 4 years experience"),
        Candidate(name="Weak", resume_text="weak@example.com HTML 1 years experience"),
    ]
    shortlist = c.shortlist(candidates, role, minimum_score=75)
    assert [r.candidate_name for r in shortlist] == ["Strong"]


def test_job_ad_validation_hebrew_age_and_military():
    validation = validate_job_ad("דרוש צעיר אחרי צבא")
    assert not validation.approved
    assert "צעיר" in validation.flags
    assert "אחרי צבא" in validation.flags


def test_job_ad_validation_english_gender():
    validation = validate_job_ad("Looking for young female support agent")
    assert not validation.approved
    assert "young" in validation.flags
    assert "female" in validation.flags


def test_schedule_skips_friday_to_sunday():
    c = client()
    role = RoleProfile(title="Python Developer", required_skills=["python"], seniority="junior")
    result = c.screen_resume(Candidate(name="Dana", resume_text="dana@example.com Python 2 years experience"), role)
    slots = c.schedule_interviews([result], start_date="2026-06-05")
    assert slots[0].start.startswith("2026-06-07")


def test_schedule_uses_business_hours():
    c = client()
    role = RoleProfile(title="Python Developer", required_skills=["python"], seniority="junior")
    results = [
        c.screen_resume(Candidate(name=f"C{i}", resume_text=f"c{i}@example.com Python 2 years experience"), role)
        for i in range(8)
    ]
    slots = c.schedule_interviews(results, start_date="2026-06-07", interview_minutes=60, daily_start=time(15, 0), daily_end=time(17, 0))
    assert slots[0].start.startswith("2026-06-07T15:00")
    assert slots[1].start.startswith("2026-06-08T15:00")


def test_format_israeli_date():
    assert format_israeli_date(date(2026, 6, 7)) == "07/06/2026"


def test_create_screening_request_chains_identifier():
    c = client()
    response = c.create_screening_request(
        Candidate(name="Dana", resume_text="dana@example.com Python SQL 4 years experience"),
        RoleProfile(title="Python Developer", required_skills=["python", "sql"], seniority="mid"),
    )
    assert response["id"] == response["result"]["candidate_id"]


def test_export_shortlist_json_hebrew_safe():
    c = client()
    role = RoleProfile(title="מנהלת חשבונות", required_skills=["חשבשבת"], seniority="mid")
    result = c.screen_resume(Candidate(name="נועה", resume_text="noa@example.com חשבשבת 4 שנות ניסיון"), role)
    payload = c.export_shortlist_json([result])
    assert "נועה" in payload
    assert "\\u05" not in payload


@pytest.mark.asyncio
async def test_async_screen_resume():
    c = AsyncRecruitmentAssistantClient(env="sandbox")
    result = await c.screen_resume(
        Candidate(name="Dana", resume_text="dana@example.com Python SQL 4 years experience"),
        RoleProfile(title="Python Developer", required_skills=["python", "sql"], seniority="mid"),
    )
    assert result.recommendation == "advance"


@pytest.mark.asyncio
async def test_async_schedule():
    c = AsyncRecruitmentAssistantClient(env="sandbox")
    result = await c.screen_resume(
        Candidate(name="Dana", resume_text="dana@example.com Python 2 years experience"),
        RoleProfile(title="Python Developer", required_skills=["python"], seniority="junior"),
    )
    slots = await c.schedule_interviews([result], start_date="2026-06-07")
    assert len(slots) == 1
