import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "backend"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "joblens.settings")

import django

django.setup()

from jobs.models import Company, Job, JobSource, Skill, JobSkill
from etl.extract.arbeitnow_extractor import fetch_jobs
from etl.transform.skill_extractor import extract_job_skills

source, _ = JobSource.objects.get_or_create(name="Arbeitnow")
jobs = fetch_jobs()

for item in jobs:

    company, _ = Company.objects.get_or_create(name=item["company_name"])

    job, _ = Job.objects.get_or_create(
        job_url=item["url"],
        defaults={
            "title": item["title"],
            "company": company,
            "source": source,
            "location": item["location"],
            "description": item["description"],
            "remote": item["remote"],
            "job_type": "FT",
        },
    )
    skills = extract_job_skills(item)

    for skill_name in skills:

        skill, _ = Skill.objects.get_or_create(name=skill_name)

        JobSkill.objects.get_or_create(job=job, skill=skill)
print("Jobs Loaded Successfully")
