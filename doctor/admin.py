from django.contrib import admin

from .models import Doctor, DoctorTimeSlot, TimeSlot

# Register your models here.
admin.site.register(Doctor)
admin.site.register(TimeSlot)
admin.site.register(DoctorTimeSlot)
