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
        title="Junior Customer Service Representative",
        required_skills=["customer service", "crm"],
        preferred_skills=["english"],
        seniority="junior",
        role_family="customer_service",
    )
    candidate = Candidate(
        name="Omer Ben David",
        resume_text="omer@example.com 052-7654321 Customer service CRM phone support Hebrew English 2 years experience",
    )
    result = client.screen_resume(candidate, role)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
