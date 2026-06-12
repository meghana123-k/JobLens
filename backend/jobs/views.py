from django.shortcuts import render
from jobs.models import Company, Job, Skill

# Create your views here.


def home(request):
    total_companies = Company.objects.count()

    total_jobs = Job.objects.count()
    total_skills = Skill.objects.count()
    companies = Company.objects.all()
    context = {
        "companies": companies,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_skills": total_skills,
    }
    return render(request, "jobs/home.html", context)


from jobs.models import Company


def companies(request):

    companies = Company.objects.all()
    context = {"companies": companies}
    return render(request, "jobs/companies.html", context)


def jobs_list(request):
    jobs_list = Job.objects.all()
    context = {"jobs_list": jobs_list}
    return render(request, "jobs/jobs_list.html", context)
