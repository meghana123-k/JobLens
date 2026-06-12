from django.shortcuts import render
from jobs.models import Company, Job
from .services import get_dashboard_stats
from .analytics_service import get_top_hiring_companies, get_top_skills

# Create your views here.


def home(request):

    stats = get_dashboard_stats()

    context = {
        **stats,
        "companies": Company.objects.all(),
        "recent_jobs": Job.objects.order_by("-id")[:5],
    }

    return render(request, "jobs/home.html", context)


def companies(request):

    companies = Company.objects.all()
    context = {"companies": companies}
    return render(request, "jobs/companies.html", context)


def jobs_list(request):
    jobs_list = Job.objects.all()
    context = {"jobs_list": jobs_list}
    return render(request, "jobs/jobs_list.html", context)


def analytics(request):

    analytical_data = { **get_top_hiring_companies(),  **get_top_skills()}

    return render(request, "jobs/analytics.html", analytical_data)
