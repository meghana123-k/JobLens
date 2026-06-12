from jobs.models import Company, Job, Skill

def get_dashboard_stats():

    return {
        "total_companies": Company.objects.count(),
        "total_jobs": Job.objects.count(),
        "total_skills": Skill.objects.count(),
    }