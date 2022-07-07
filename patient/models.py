from datetime import datetime  
from datetime import timedelta
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

# 3rd party module imports
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

# Create your models here.


class Patient(models.Model):
    phone_no = PhoneNumberField(null=False, blank=False, unique=True)

    def __str__(self):
        return self.phone_no.as_e164


class PatientProfile(models.Model):
    patient = models.OneToOneField(Patient,
                                   primary_key=True,
                                   on_delete=models.CASCADE,
                                   help_text=('Patient (Required).'),
                                   )
    first_name = models.CharField(max_length=100, default="")
    middle_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    age = models.IntegerField(default=0)
    address = models.CharField(max_length=100, default="")
    email = models.EmailField(max_length=100, default="")
    gender = models.CharField(max_length=30, default="Male")
    blood_group = models.CharField(max_length=30, default="")

    def __str__(self):
        return f"{self.patient.phone_no} -> {self.first_name} {self.middle_name} {self.last_name}"


# @receiver(post_save, sender=Patient)
# def create_or_update_patient_profile(sender, instance, created, **kwargs):
#     if created:
#         PatientProfile.objects.create(patient=instance)
#     instance.patientprofile.save()

def get_expiry_time():
    return timezone.now() + timedelta(minutes=5)

class OTP(models.Model):
    phone_no=PhoneNumberField(null=False, blank=False)
    secret = models.CharField(max_length=100, default="")
    otp = models.CharField(max_length=100, default="")

    created_at = models.DateTimeField(default=datetime.now)
    expires_at = models.DateTimeField(default=get_expiry_time)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone_no} -> {self.otp}"
