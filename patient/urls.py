from django.urls import path
from .views import home, get_otp, verify_otp, save_patient_profile, check_slot_availability, book_slot, get_doctors_for_day, get_available_slots, check_available_slots, patient_profile, appointment_details, appointment_history_get_otp, appointment_history_verify_otp, appointment_history,appointment_home,check_available_slots_new,resend_otp,resend_otp_appointment_history

app_name = 'patient'

urlpatterns = [
    path('', home, name='home'),
    #     path('get-otp/', get_otp, name='get-otp'),
    #     path('verify-otp/', verify_otp, name='verify-otp'),
    path('save-patient-profile/', save_patient_profile,
         name='save-patient-profile'),
    path('check-slot-availability/',
         check_slot_availability, name='check-slot-availability'),
    path('book-slot/', book_slot, name='book-slot'),
    path('get-doctors-for-day/', get_doctors_for_day, name='get-doctors-for-day'),
    path('get-available-slots/', get_available_slots, name='get-available-slots'),

     path('appointment-home',appointment_home,name='appointment-home'),
#     path('check-available-slots/', check_available_slots,
#          name='check-available-slots'),
     path('check-available-slots/', check_available_slots_new,
     name='check-available-slots'),
    path('get-otp/', get_otp, name='get-otp'),
    path('verify-otp/', verify_otp, name='verify-otp'),
     path('resend-otp/',resend_otp,name='resend-otp'),

    path('patient-profile/', patient_profile, name='patient-profile'),
    path('appointment-details/<int:appointment_id>/',
         appointment_details, name='appointment-details'),

    path('appointment-history-get-otp/', appointment_history_get_otp,
         name='appointment-history-get-otp'),
    path('appointment-history-verify-otp/', appointment_history_verify_otp,
         name='appointment-history-verify-otp'),
    path('appointment-history/', appointment_history, name='appointment-history'),
    path('resend-otp-appointment-history/',resend_otp_appointment_history,name='resend-otp-appointment-history'),
]
