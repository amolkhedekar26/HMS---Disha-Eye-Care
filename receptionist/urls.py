from django.urls import path
from .views import home, add_receptionist, generate_daily_bookings_new, time_slots, appointments, appointment_details, patient_details, doctor_details, patients, doctors, receptionist_profile, daily_slot_schedule, daily_slot_schedule_details, generate_daily_slot_schedule, appointment_create,book_slot,patient_create,select_patient,enter_patient_message,generate_prescription_and_invoice,prescription_and_invoice_details

app_name = 'receptionist'

urlpatterns = [
    path('', home, name='home'),
    path('add-receptionist/', add_receptionist, name='add-receptionist'),
    path('generate-daily-bookings/', generate_daily_bookings_new,
         name='generate-daily-bookings'),
]

# URL for Time Slots
urlpatterns += [
    path('time-slots/', time_slots, name='time-slots'),
]

# URL for Daily Schedules of Slots
urlpatterns += [
    path('daily-slots-schedule/', daily_slot_schedule,
         name='daily-slots-schedule'),
    path('daily-slots-schedule/<int:id>/details/',
         daily_slot_schedule_details, name='daily-slots-schedule-details'),
    path('generate-daily-slot-schedule/', generate_daily_slot_schedule,
         name='generate-daily-slot-schedule'),
]

# URL for Appointments
urlpatterns += [
    path('appointments/', appointments, name='appointments'),
    path('appointments/<int:id>/details/',
         appointment_details, name='appointment-details'),
    path('appointments/create/', appointment_create, name='create-appointment'),
    path('book-slot/', book_slot, name='book-slot'),
    path('select-patient/', select_patient, name='select-patient'),
    path('enter-patient-message/<int:id>/', enter_patient_message, name='enter-patient-message'),
    path('generate-prescription-and-invoice/<int:id>/',
         generate_prescription_and_invoice, name='generate-prescription-and-invoice'),
    path('prescription-and-invoice/<int:id>/details/',prescription_and_invoice_details,name='prescription-and-invoice-details'),
    
    
]

# URL for Patients
urlpatterns += [
    path('patients/', patients, name='patients'),
    path('patients/<int:id>/details/', patient_details, name='patient-details'),
    path('patients/create/',patient_create,name='create-patient')
]

# URL for Doctors
urlpatterns += [
    path('doctors/', doctors, name='doctors'),
    path('doctors/<int:id>/details/', doctor_details, name='doctor-details'),
]

# URL for Profile
urlpatterns += [
    path('receptionist-profile/', receptionist_profile,
         name='receptionist-profile'),
]
