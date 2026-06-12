import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "backend"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "joblens.settings")

import django

django.setup()

from etl_logs.models import ETLLog
from jobs.models import Company, Job, JobSource, Skill, JobSkill
from etl.extract.arbeitnow_extractor import fetch_jobs
from etl.transform.skill_extractor import extract_job_skills


def run_etl():

    start_time = time.time()

    try:

        source, _ = JobSource.objects.get_or_create(name="Arbeitnow")

        jobs = fetch_jobs()

        records_processed = 0

        for item in jobs:

            company, _ = Company.objects.get_or_create(name=item["company_name"])

            job, created = Job.objects.get_or_create(
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

            if created:
                records_processed += 1

            skills = extract_job_skills(item)

            for skill_name in skills:

                skill, _ = Skill.objects.get_or_create(name=skill_name)

                JobSkill.objects.get_or_create(
                    job=job,
                    skill=skill,
                )

        execution_time = round(time.time() - start_time, 2)

        ETLLog.objects.create(
            source_name="Arbeitnow",
            records_processed=records_processed,
            status="SUCCESS",
            execution_time=execution_time,
            error_message="",
        )

        print(f"SUCCESS | {records_processed} jobs loaded")

    except Exception as e:

        execution_time = round(time.time() - start_time, 2)

        ETLLog.objects.create(
            source_name="Arbeitnow",
            records_processed=0,
            status="FAILED",
            execution_time=execution_time,
            error_message=str(e),
        )

        print(f"FAILED | {e}")


if __name__ == "__main__":
    run_etl()