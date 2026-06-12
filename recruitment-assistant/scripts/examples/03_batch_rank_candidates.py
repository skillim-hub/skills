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
        title="Mid Python Developer",
        required_skills=["python", "sql"],
        preferred_skills=["react"],
        seniority="mid",
        role_family="software",
    )
    candidates = [
        Candidate(name="Dana", resume_text="dana@example.com Python SQL React 4 years experience"),
        Candidate(name="Avi", resume_text="avi@example.com Python 2 years experience"),
        Candidate(name="Maya", resume_text="maya@example.com Python SQL 5 years experience"),
    ]
    ranked = client.rank_candidates(candidates, role)
    print(json.dumps([result.to_dict() for result in ranked], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
