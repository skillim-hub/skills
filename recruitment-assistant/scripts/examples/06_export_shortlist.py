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
    role = RoleProfile(title="מנהלת חשבונות", required_skills=["חשבשבת", "אקסל"], seniority="mid", role_family="accounting")
    candidates = [
        Candidate(name="נועה", resume_text="noa@example.co.il חשבשבת אקסל 5 שנות ניסיון"),
        Candidate(name="יעל", resume_text="yael@example.co.il אקסל 2 שנות ניסיון"),
    ]
    shortlist = client.shortlist(candidates, role, minimum_score=75)
    print(json.dumps([result.to_dict() for result in shortlist], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
