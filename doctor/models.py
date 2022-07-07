from time import strftime
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from users.models import User

# Create your models here.


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_no = PhoneNumberField(null=False, blank=False, unique=True)
    address = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    fees = models.CharField(max_length=100)
    timings = models.CharField(max_length=100)
    profile_image = models.ImageField(
        upload_to='doctor_profile_pic/', blank=True)
    certificate_image = models.ImageField(
        upload_to='doctor_certificate/', blank=True)

    def __str__(self):
        return self.user.email + self.first_name + " " + self.last_name


class TimeSlot(models.Model):
    weekdays_choices = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )
    
    day = models.CharField(
        max_length=100, choices=weekdays_choices, default=weekdays_choices[0])
    start_time = models.TimeField()
    end_time = models.TimeField()
    half_time = models.CharField(
        max_length=50,  blank=True, null=True)
    deleted=models.BooleanField(default=False)

    @property
    def get_time_slot(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"

    @property
    def get_time_slot_with_day(self):
        return f"{self.day} ... {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"

    def __str__(self):
        return self.day + " => " + str(self.start_time) + " - " + str(self.end_time) + " " + str(self.half_time)


class DoctorTimeSlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    deleted=models.BooleanField(default=False)

    class Meta:
        unique_together = (('doctor', 'time_slot'),)

    def __str__(self):
        return self.doctor.email + " " + str(self.time_slot)
