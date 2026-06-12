from django.shortcuts import render
from .models import ETLLog


def etl_logs(request):

    logs = ETLLog.objects.order_by("-created_at")

    total_runs = ETLLog.objects.count()

    success_runs = ETLLog.objects.filter(status="SUCCESS").count()

    failed_runs = ETLLog.objects.filter(status="FAILED").count()

    context = {
        "logs": logs,
        "total_runs": total_runs,
        "success_runs": success_runs,
        "failed_runs": failed_runs,
    }

    return render(
        request,
        "etl_logs/etl_logs.html",
        context,
    )
