from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Patient, PatientProfile


@receiver(post_save, sender=Patient, dispatch_uid='patient.create_or_update_patient_profile')
def create_or_update_patient_profile(sender, instance, created, **kwargs):
    if created:
        PatientProfile.objects.create(patient=instance)
    instance.patientprofile.save()
# def create_patient_profile(sender, instance, created, **kwargs):
#     if created:
#         PatientProfile.objects.create(patient=instance)


# @receiver(post_save, sender=Patient, dispatch_uid='patient.save_patient_profile')
# def save_patient_profile(sender, instance, **kwargs):
#     instance.patientprofile.save()
