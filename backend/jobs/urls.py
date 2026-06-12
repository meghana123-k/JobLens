from django.urls import path
from .views import home, companies, jobs_list

urlpatterns = [
    path("", home, name="home"),
    path("companies/", companies, name="companies"),
    path("jobs/", jobs_list, name="jobs_list")
]