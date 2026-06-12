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
    role = RoleProfile(title="Python Developer", required_skills=["python"], seniority="junior", role_family="software")
    candidates = [
        Candidate(name="Dana", resume_text="dana@example.com Python 2 years experience"),
        Candidate(name="Omer", resume_text="omer@example.com Python SQL 3 years experience"),
    ]
    results = client.rank_candidates(candidates, role)
    slots = client.schedule_interviews(results, start_date="2026-06-05", interview_minutes=45, channel="video")
    print(json.dumps([slot.to_dict() for slot in slots], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
