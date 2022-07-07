import uuid
from django.db import models

from doctor.models import DoctorTimeSlot
from patient.models import Patient
# Create your models here.


class DailySlotBooking(models.Model):
    date = models.DateField()
    doctor_time_slot = models.ForeignKey(
        DoctorTimeSlot, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} {self.doctor_time_slot.doctor} {self.doctor_time_slot.time_slot} {self.status}"

APPOINTMENT_STATUS_CHOICES = (('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'))

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    daily_slot_booking = models.ForeignKey(
        DailySlotBooking, on_delete=models.DO_NOTHING)
    message = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    @property
    def is_cancelled(self):
        return self.status == 'CANCELLED'
    
    @property
    def is_pending(self):
        return self.status == 'PENDING'
    

    def __str__(self):
        return f"{self.patient} {self.daily_slot_booking} {self.status}"


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=200)
    symptoms = models.CharField(max_length=200)
    prescription_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.appointment} {self.content} {self.symptoms}"


class Invoice(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.DO_NOTHING)
    invoice_no=models.UUIDField(
         default = uuid.uuid4,
         editable = False)

    consultation_fee=models.PositiveIntegerField()
    medicine_charges=models.PositiveIntegerField()
    lab_fee=models.PositiveIntegerField()
    other_charges=models.PositiveIntegerField()

    total_amount = models.PositiveIntegerField()

    status=models.CharField(max_length=50,null=True,blank=True)

    invoice_date = models.DateField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.appointment} {self.total_amount} {self.status}"
