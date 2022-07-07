from django.contrib import admin

from .models import OTP, Patient, PatientProfile

# Register your models here.
admin.site.register(Patient)
admin.site.register(PatientProfile)
admin.site.register(OTP)
