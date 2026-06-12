from recruitment_assistant.client import *  # noqa: F401,F403

if __name__ == "__main__":
    import json
    from recruitment_assistant import Candidate, RecruitmentAssistantClient, RoleProfile

    client = RecruitmentAssistantClient(env="sandbox")
    result = client.create_screening_request(
        Candidate(name="Example", resume_text="example@example.com 052-1234567 Python SQL 4 years experience"),
        RoleProfile(title="Python Developer", required_skills=["python", "sql"], seniority="mid"),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
