from django.urls import path
from .views import etl_logs

urlpatterns = [
    path("", etl_logs, name="etl_logs"),
]
