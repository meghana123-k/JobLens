from django.db import models


# Create your models here.
class JobSource(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Job(models.Model):

    JOB_TYPES = [
        ("FT", "Full Time"),
        ("PT", "Part Time"),
        ("IN", "Internship"),
        ("CT", "Contract"),
    ]

    title = models.CharField(max_length=255)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")

    source = models.ForeignKey(JobSource, on_delete=models.CASCADE)

    location = models.CharField(max_length=255, blank=True)

    salary_min = models.IntegerField(null=True, blank=True)

    salary_max = models.IntegerField(null=True, blank=True)

    experience_years = models.IntegerField(null=True, blank=True)

    job_type = models.CharField(max_length=2, choices=JOB_TYPES)

    job_url = models.URLField(unique=True)

    description = models.TextField(blank=True)

    posted_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    skills = models.ManyToManyField(Skill, through="JobSkill")

    def __str__(self):
        return self.title


class JobSkill(models.Model):

    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("job", "skill")
