from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Job)
admin.site.register(Company)
admin.site.register(Skill)
admin.site.register(JobSource)
admin.site.register(JobSkill)