# arbeitnow_extractor.py
import requests
from etl.transform.skill_extractor import SkillExtractor

URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_jobs():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["data"]


if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"Total Jobs Fetched: {len(jobs)}\n")

    extractor = SkillExtractor(
        enable_fuzzy=False, enable_ner=False
    )  # flip to True if desired

    # Show available fields and a few examples
    print("Available Fields:\n")
    print(jobs[0].keys())
    print(jobs[0].get("tags", []))
    print()

    for i in range(min(5, len(jobs))):
        title = jobs[i].get("title", "")
        tags = jobs[i].get("tags", [])
        skills = extractor.extract_job_skills(jobs[i])
        print(title)
        print("Tags:", tags)
        print("Extracted Skills:", skills)
        print("-" * 50)
