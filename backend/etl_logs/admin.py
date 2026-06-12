from django.contrib import admin
from .models import *
# Register your models here.

from django.contrib import admin
from .models import ETLLog


@admin.register(ETLLog)
class ETLLogAdmin(admin.ModelAdmin):

    list_display = (
        "source_name",
        "records_processed",
        "status",
        "execution_time",
        "created_at",
    )

    list_filter = (
        "status",
        "source_name",
    )

    search_fields = ("source_name",)