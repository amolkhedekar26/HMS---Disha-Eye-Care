from django.contrib import admin
from .models import Appointment, DailySlotBooking, Invoice, Prescription

# Register your models here.
admin.site.register(DailySlotBooking)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Invoice)
