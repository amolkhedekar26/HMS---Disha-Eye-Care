from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

User = get_user_model()


class Receptionist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_no = PhoneNumberField(blank=False, null=False, unique=True)
    address = models.CharField(max_length=100)
    profile_image = models.ImageField(
        upload_to='receptionist_profile_pic/', blank=True)

    def __str__(self):
        return self.user.email + " -> "+self.first_name
