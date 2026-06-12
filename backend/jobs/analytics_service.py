from jobs.models import Company, Skill
from django.db.models import Count


def get_top_hiring_companies():
    return {
        "top_companies": Company.objects.annotate(job_count=Count("jobs")).order_by(
            "-job_count"
        )
    }

def get_top_skills():

    return {
        "top_skills": (
            Skill.objects.annotate(job_count=Count("jobskill")).order_by("-job_count")
        )
    }
