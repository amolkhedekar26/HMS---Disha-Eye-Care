from django.urls import path
from .views import home, add_doctor, add_time_slots, time_slots, edit_time_slot, delete_time_slot, add_time_slot,my_appointments,appointment_details,my_patients,patient_details,doctor_profile

app_name = 'doctor'

urlpatterns = [
    path('', home, name='home'),
    path('add-doctor/', add_doctor, name='add-doctor'),
    path('add-time-slots/', add_time_slots, name='add-time-slots'),
]

# URL for Time Slots
urlpatterns += [
    path('time-slots/', time_slots, name='time-slots'),
    path('time-slot/<int:id>/edit/', edit_time_slot, name='edit-time-slot'),
    path('time-slot/<int:id>/delete/', delete_time_slot, name='delete-time-slot'),
    path('add-time-slot/', add_time_slot, name='add-time-slot'),
]

# URL for My Appointments
urlpatterns += [
    path('my-appointments/', my_appointments, name='my-appointments'),
    path('my-appointments/<int:id>/details/', appointment_details, name='appointment-details'),
]

# URL for My Patients
urlpatterns += [
    path('my-patients/', my_patients, name='my-patients'),
    path('my-patients/<int:id>/details/', patient_details, name='patient-details'),
]

# URL for Doctor Profile
urlpatterns += [
    path('doctor-profile/', doctor_profile, name='doctor-profile'),
]