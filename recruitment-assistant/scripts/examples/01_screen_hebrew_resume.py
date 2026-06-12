from __future__ import annotations

import argparse
import json
import os

from recruitment_assistant import Candidate, RecruitmentAssistantClient, RoleProfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RECRUITMENT_ASSISTANT_ENV", "sandbox"))
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    api_key = os.getenv("RECRUITMENT_ASSISTANT_API_KEY")
    client = RecruitmentAssistantClient(env=args.env, api_key=api_key)
    role = RoleProfile(
        title="מנהלת חשבונות",
        required_skills=["חשבשבת", "אקסל"],
        preferred_skills=["שכר", "פריוריטי"],
        seniority="mid",
        role_family="accounting",
        salary_min_ils=9000,
        salary_max_ils=12000,
    )
    candidate = Candidate(
        name="נועה כהן",
        resume_text="noa@example.co.il 054-1234567 חשבשבת אקסל התאמות בנקים 5 שנות ניסיון",
    )
    response = client.create_screening_request(candidate, role)
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
