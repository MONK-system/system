from django.contrib import admin

# Register your models here.

from .models import Doctor, Patient, Project, Vitals

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Project)
admin.site.register(Vitals)
