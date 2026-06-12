from django.db import models

# Create your models here.
class ETLLog(models.Model):

    source_name = models.CharField(max_length=100)

    records_processed = models.IntegerField(default=0)

    STATUS_CHOICES = [
    ("SUCCESS", "SUCCESS"),
    ("FAILED", "FAILED"),
]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    execution_time = models.FloatField()

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_name} - {self.status}"
