import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from datetime import date, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django. db. models import Q


from appointment.models import Appointment, DailySlotBooking, Invoice, Prescription
from doctor.models import Doctor, DoctorTimeSlot
from patient.repositories.patient_profile import PatientProfileRepository
from patient.repositories.patient import PatientRepository
from receptionist.models import Receptionist
from patient.models import Patient
from .forms import AddPrescriptionForm, ChangeDailySlotStatus, CreateNewAppointmentForm, DailyBookingForm, DailySlotScheduleForm, EditReceptionistForm, EnterPatientMessageForm,  EnterPatientprofileForm, GenerateDailySlotScheduleForm, GenerateInvoiceForm, GetAppointmentsForm, GetPatientsForm, GetTimeSlotForm, PatientPhoneNoForm, ReceptionistUserForm, ReceptionistForm

# Create your views here.

User = get_user_model()

USER_GROUP = {
    'RECEPTIONIST': 'RECEPTIONIST',
}


def home(request):
    return render(request, 'receptionist/index.html')


def add_receptionist(request):
    receptionist_user_form = ReceptionistUserForm()
    receptionist_form = ReceptionistForm()
    template_context = {
        'receptionist_user_form': receptionist_user_form,
        'receptionist_form': receptionist_form
    }
    if request.method == 'POST':
        receptionist_user_form = ReceptionistUserForm(request.POST)
        receptionist_form = ReceptionistForm(request.POST, request.FILES)
        print(receptionist_user_form.errors)
        print(receptionist_form.errors)
        if receptionist_user_form.is_valid() and receptionist_form.is_valid():

            receptionist_user = receptionist_user_form.save()
            receptionist_user.set_password(receptionist_user.password)
            receptionist_user.save()

            receptionist = receptionist_form.save(commit=False)
            receptionist.user = receptionist_user
            receptionist = receptionist.save()

            add_user_to_group(receptionist_user, 'RECEPTIONIST')

            return HttpResponse('Receptionist added successfully')
    return render(request, 'receptionist/add_receptionist.html', context=template_context)


def add_user_to_group(user, group):
    group = Group.objects.get(name=USER_GROUP[group])
    group.user_set.add(user)


def generate_daily_bookings(request):
    daily_booking_form = DailyBookingForm()
    template_context = {
        'daily_booking_form': daily_booking_form
    }
    if request.method == 'POST':
        selected_doctors = request.POST.getlist('doctors')
        input_day = request.POST.get('day-toggler')
        input_number_of_days = request.POST.get('input-number')
        if input_day == 'today':
            number_of_days = 0
        elif input_day == 'tomorrow':
            number_of_days = 1
        else:
            number_of_days = int(input_number_of_days)
        print(get_dates_from_number_of_days(number_of_days))
        print(selected_doctors)
        doctors = Doctor.objects.filter(id__in=selected_doctors)
        print(doctors)
        for doctor in doctors:
            doctor = User.objects.get(email=doctor.user.email)

            doctor_time_slots = DoctorTimeSlot.objects.filter(
                doctor=doctor, deleted=False)
            print(doctor_time_slots)
            for day_date in get_dates_from_number_of_days(number_of_days):
                for doctor_time_slot in doctor_time_slots:
                    DailySlotBooking.objects.get_or_create(
                        date=day_date,
                        doctor_time_slot=doctor_time_slot,
                        status='AVAILABLE'
                    )
        messages.success(request, 'Daily bookings generated successfully')
        
        return HttpResponse('Daily Bookings generated successfully')
    return render(request, 'receptionist/generate_daily_bookings.html', context=template_context)

def get_working_days(dates):
    return [date for date in dates if date.weekday() < 6]


def get_dates_from_number_of_days(number_of_days):
    if number_of_days == 0:
        return get_working_days([date.today()])
    elif number_of_days == 1:
        return get_working_days([date.today() + timedelta(days=1)])
    else:
        return get_working_days([date.today() + timedelta(days=i) for i in range(number_of_days)])


def get_next_working_day(input_date):
    if input_date.weekday() == 6:
        return input_date + timedelta(days=1)
    else:
        return input_date


def get_n_working_days(n):
    import datetime
    today = datetime.date.today()
    next_working_days = []
    for i in range(n):
        next_day = today + datetime.timedelta(days=i)
        d = get_next_working_day(next_day)
        next_working_days.append(d)
    return next_working_days


def generate_daily_bookings_new(request):
    daily_booking_form = DailyBookingForm()
    template_context = {
        'daily_booking_form': daily_booking_form
    }
    if request.method == 'POST':
        selected_doctors = request.POST.getlist('doctors')
        input_day = request.POST.get('day-toggler')
        input_number_of_days = request.POST.get('input-number')
        if input_day == 'today':
            number_of_days = 0
        elif input_day == 'tomorrow':
            number_of_days = 1
        else:
            number_of_days = int(input_number_of_days)
        
        doctors = Doctor.objects.filter(id__in=selected_doctors)
       
        return HttpResponse('Daily Bookings generated successfully')
    return render(request, 'receptionist/generate_daily_bookings.html', context=template_context)


def get_today_day():
    return datetime.date.today().strftime('%A')


def get_first_doctor():
    return Doctor.objects.first()


def time_slots_default_day_doctor(request):
    template_page = 'receptionist/time_slots.html'

    get_time_slots_form = GetTimeSlotForm()

    page = request.GET.get('page', 1)
    selected_day = request.GET.get('days', get_today_day())
    if not selected_day:
        selected_day = get_today_day()

    selected_doctor = None
    selected_doctor_id = request.GET.get('doctors', get_first_doctor().id)
    if selected_doctor_id:
        selected_doctor = Doctor.objects.filter(id=selected_doctor_id).first()
    doctor_time_slots = DoctorTimeSlot.objects.filter(doctor=selected_doctor.user,
                                                      time_slot__day=selected_day, time_slot__deleted=False)

    PAGE_OFFSET = 5
    paginator = Paginator(doctor_time_slots, PAGE_OFFSET)
    try:
        slots = paginator.page(page)
    except PageNotAnInteger:
        slots = paginator.page(1)
    except EmptyPage:
        slots = paginator.page(paginator.num_pages)

    template_context = {
        'get_time_slots_form': get_time_slots_form,
        'doctor_time_slots': slots,
        'selected_day': selected_day,
        'selected_doctor': selected_doctor,
    }

    return render(request, template_page, context=template_context)


def time_slots(request):
    template_page = 'receptionist/time_slots.html'

    get_time_slots_form = GetTimeSlotForm()

    page = request.GET.get('page', 1)
    selected_day = request.GET.get('days', get_today_day())
    if not selected_day:
        selected_day = get_today_day()

    selected_doctor = None
    selected_doctor_id = request.GET.get('doctors', None)
    if selected_doctor_id:
        selected_doctor = Doctor.objects.filter(id=selected_doctor_id).first()

    
    selected_search_filters = request.GET.get('search-time-slots', None)

    doctor_time_slots = DoctorTimeSlot.objects.filter(
        time_slot__day=selected_day, time_slot__deleted=False)

    if selected_search_filters:
        doctor_time_slots = doctor_time_slots.filter(
            Q(time_slot__start_time__icontains=selected_search_filters) | Q(time_slot__end_time__icontains=selected_search_filters) | Q(time_slot__half_time__icontains=selected_search_filters) |
            Q(doctor__doctor__first_name__icontains=selected_search_filters) | Q(
                doctor__doctor__last_name__icontains=selected_search_filters)
        )

    if selected_doctor:
        doctor_time_slots = doctor_time_slots.filter(
            doctor=selected_doctor.user)

        if selected_search_filters:
            doctor_time_slots = doctor_time_slots.filter(
                Q(time_slot__start_time__icontains=selected_search_filters) | Q(time_slot__end_time__icontains=selected_search_filters) | Q(time_slot__half_time__icontains=selected_search_filters))

    PAGE_OFFSET = 5
    paginator = Paginator(doctor_time_slots, PAGE_OFFSET)
    try:
        slots = paginator.page(page)
    except PageNotAnInteger:
        slots = paginator.page(1)
    except EmptyPage:
        slots = paginator.page(paginator.num_pages)

    template_context = {
        'get_time_slots_form': get_time_slots_form,
        'doctor_time_slots': slots,
        'selected_day': selected_day,
        'selected_doctor': selected_doctor,
    }

    return render(request, template_page, context=template_context)


def appointments(request):
    template_page = 'receptionist/appointments.html'

    get_appointments_form = GetAppointmentsForm()

    selected_search_filters = request.GET.get('search-appointments', None)

    appointments = Appointment.objects.all(
    ).order_by('-created_at')

    if selected_search_filters:
        appointments = appointments.filter(
            Q(patient__patientprofile__first_name__icontains=selected_search_filters) | Q(patient__patientprofile__last_name__icontains=selected_search_filters) | Q(daily_slot_booking__doctor_time_slot__doctor__doctor__first_name__icontains=selected_search_filters) | Q(
                daily_slot_booking__doctor_time_slot__doctor__doctor__last_name__icontains=selected_search_filters) | Q(daily_slot_booking__doctor_time_slot__time_slot__start_time__icontains=selected_search_filters) | Q(daily_slot_booking__doctor_time_slot__time_slot__end_time__icontains=selected_search_filters)
        )

    page = request.GET.get('page', 1)

    selected_date = request.GET.get('date', None)
    selected_appointment_status = request.GET.get('appointment_status', 'ALL')

    if selected_date and selected_appointment_status:
        if selected_appointment_status == 'ALL':
            appointments = appointments.filter(
                daily_slot_booking__date=selected_date,
            )
        else:
            appointments = appointments.filter(
                daily_slot_booking__date=selected_date,
                status=selected_appointment_status
            )

    if selected_date:
        appointments = appointments.filter(
            daily_slot_booking__date=selected_date
        )

    if selected_appointment_status:
        if selected_appointment_status == "ALL":
            appointments = appointments
        else:
            appointments = appointments.filter(
                status=selected_appointment_status
            )

    PAGE_OFFSET = 5
    paginator = Paginator(appointments, PAGE_OFFSET)
    try:
        appointments = paginator.page(page)
    except PageNotAnInteger:
        appointments = paginator.page(1)
    except EmptyPage:
        appointments = paginator.page(paginator.num_pages)

    template_context = {
        'appointments': appointments,
        'get_appointments_form': get_appointments_form,
        'selected_date': selected_date,
        'selected_appointment_status': selected_appointment_status,
    }
    return render(request, template_page, context=template_context)


def appointment_details(request, id):
    template_page = 'receptionist/appointment_details.html'
    appointment = Appointment.objects.filter(id=id).first()
    invoice=None
    if appointment.status == "COMPLETED":
        invoice=Invoice.objects.filter(appointment=appointment).first()
    template_context = {
        'appointment': appointment,
        'invoice':invoice,
    }
    return render(request, template_page, context=template_context)


def patients(request):
    template_page = 'receptionist/patients.html'

    get_patients_form = GetPatientsForm()

    patients_list = Patient.objects.all().distinct()

    selected_doctor_id = request.GET.get('doctors', None)
    if selected_doctor_id:
        doctor = Doctor.objects.filter(id=selected_doctor_id).first()
        my_appointments = Appointment.objects.filter(
            daily_slot_booking__doctor_time_slot__doctor=doctor.user,
        )
        my_patients = my_appointments.values_list(
            'patient', flat=True).distinct()
        patients_list = Patient.objects.filter(id__in=my_patients)

    selected_search_filters = request.GET.get('search-patients', None)
    if selected_search_filters:
        patients_list = patients_list.filter(
            Q(patientprofile__first_name__icontains=selected_search_filters) | Q(patientprofile__last_name__icontains=selected_search_filters) | Q(
                phone_no__icontains=selected_search_filters) | Q(patientprofile__address__icontains=selected_search_filters)
        )

    page = request.GET.get('page', 1)

    PAGE_OFFSET = 5
    paginator = Paginator(patients_list, PAGE_OFFSET)
    try:
        patients_arr = paginator.page(page)
    except PageNotAnInteger:
        patients_arr = paginator.page(1)
    except EmptyPage:
        patients_arr = paginator.page(paginator.num_pages)

    template_context = {
        'patients': patients_arr,
        'get_patients_form': get_patients_form,
    }

    return render(request, template_page, context=template_context)


def patient_details(request, id):
    template_page = 'receptionist/patient_details.html'
    patient = Patient.objects.filter(id=id).first()
    template_context = {
        'patient': patient
    }
    return render(request, template_page, context=template_context)


def doctors(request):
    template_page = 'receptionist/doctors.html'

    doctors_list = Doctor.objects.all().distinct()

    selected_search_filters = request.GET.get('search-doctors', None)

    if selected_search_filters:
        doctors_list = doctors_list.filter(
            Q(first_name__icontains=selected_search_filters) | Q(last_name__icontains=selected_search_filters) | Q(phone_no__icontains=selected_search_filters) | Q(address__icontains=selected_search_filters) |
            Q(specialization__icontains=selected_search_filters) | Q(
                qualification__icontains=selected_search_filters) | Q(experience__icontains=selected_search_filters)
        )

    page = request.GET.get('page', 1)

    PAGE_OFFSET = 5
    paginator = Paginator(doctors_list, PAGE_OFFSET)
    try:
        doctors_arr = paginator.page(page)
    except PageNotAnInteger:
        doctors_arr = paginator.page(1)
    except EmptyPage:
        doctors_arr = paginator.page(paginator.num_pages)

    template_context = {
        'doctors': doctors_arr,
    }
    return render(request, template_page, context=template_context)


def doctor_details(request, id):
    template_page = 'receptionist/doctor_details.html'
    doctor = Doctor.objects.filter(id=id).first()
    template_context = {
        'doctor': doctor
    }
    return render(request, template_page, context=template_context)


def receptionist_profile(request):
    template_page = 'receptionist/receptionist_profile.html'

    
    receptionist = Receptionist.objects.filter(user=request.user).first()
    receptionist_profile_form = EditReceptionistForm(instance=receptionist)
    if request.method == 'POST':
        receptionist_profile_form = EditReceptionistForm(
            request.POST, instance=receptionist)
        if receptionist_profile_form.is_valid():

            # data={
            #     'first_name': receptionist_profile_form.cleaned_data['first_name'],
            #     'middle_name': receptionist_profile_form.cleaned_data['middle_name'],
            #     'last_name': receptionist_profile_form.cleaned_data['last_name'],

            #     'phone_no': receptionist_profile_form.cleaned_data['phone_no'],
            #     'address': receptionist_profile_form.cleaned_data['address'],

            #     'profile_image': receptionist_profile_form.cleaned_data['profile_image'],
            # }

            receptionist_profile_obj = receptionist_profile_form.save(
                commit=False)
            if 'profile_image' in request.FILES:
                receptionist_profile_obj.profile_image = request.FILES['profile_image']

            receptionist_profile_obj.save()

            messages.success(request, 'Profile updated successfully')
            return redirect('receptionist:receptionist-profile')


    template_context = {
        'receptionist': receptionist,
        'receptionist_profile_form': receptionist_profile_form,
    }
    return render(request, template_page, context=template_context)


def daily_slot_schedule(request):
    template_page = 'receptionist/daily_slot_schedule.html'

    daily_slot_schedule_form = DailySlotScheduleForm()

    daily_slots_bookings = DailySlotBooking.objects.all().order_by('-date')

    selected_search_filters = request.GET.get('search-daily-slots', None)
    if selected_search_filters:
        daily_slots_bookings = daily_slots_bookings.filter(
            Q(doctor_time_slot__time_slot__start_time__icontains=selected_search_filters) |
            Q(doctor_time_slot__time_slot__end_time__icontains=selected_search_filters) |
            Q(doctor_time_slot__doctor__doctor__first_name__icontains=selected_search_filters) |
            Q(doctor_time_slot__doctor__doctor__last_name__icontains=selected_search_filters) |
            Q(status__icontains=selected_search_filters)
        )

    selected_date = request.GET.get('date', None)
    selected_doctor_id = request.GET.get('doctors', None)
    selected_daily_slot_status = request.GET.get('daily_slot_status', None)

    doctor = Doctor.objects.filter(id=selected_doctor_id).first()

    if selected_date and selected_doctor_id and selected_daily_slot_status:
        doctor = Doctor.objects.filter(id=selected_doctor_id).first()
        daily_slots_bookings = DailySlotBooking.objects.filter(
            date=selected_date, doctor_time_slot__doctor=doctor.user, status=selected_daily_slot_status).order_by('-date')

    if selected_doctor_id and selected_daily_slot_status:
        doctor = Doctor.objects.filter(id=selected_doctor_id).first()
        daily_slots_bookings = DailySlotBooking.objects.filter(
            doctor_time_slot__doctor=doctor.user, status=selected_daily_slot_status).order_by('-date')

    if selected_date and selected_daily_slot_status:
        daily_slots_bookings = DailySlotBooking.objects.filter(
            date=selected_date, status=selected_daily_slot_status).order_by('-date')

    if selected_date and selected_doctor_id:
        doctor = Doctor.objects.filter(id=selected_doctor_id).first()
        daily_slots_bookings = DailySlotBooking.objects.filter(
            date=selected_date, doctor_time_slot__doctor=doctor.user).order_by('-date')

    if selected_date:
        daily_slots_bookings = daily_slots_bookings.filter(
            date=selected_date).order_by('-date')

    if selected_doctor_id:
        doctor = Doctor.objects.filter(id=selected_doctor_id).first()
        daily_slots_bookings = daily_slots_bookings.filter(
            doctor_time_slot__doctor=doctor.user).order_by('-date')

    if selected_daily_slot_status:
        daily_slots_bookings = daily_slots_bookings.filter(
            status=selected_daily_slot_status).order_by('-date')

    page = request.GET.get('page', 1)

    PAGE_OFFSET = 5
    paginator = Paginator(daily_slots_bookings, PAGE_OFFSET)
    try:
        daily_slots_bookings_arr = paginator.page(page)
        daily_slots_bookings_arr.adjusted_elided_pages = paginator.get_elided_page_range(
            page)
    except PageNotAnInteger:
        daily_slots_bookings_arr = paginator.page(1)
    except EmptyPage:
        daily_slots_bookings_arr = paginator.page(paginator.num_pages)

    template_context = {
        'daily_slot_schedule_form': daily_slot_schedule_form,
        'daily_slots_bookings': daily_slots_bookings_arr,
        'page_obj': daily_slots_bookings_arr,
        'selected_date': selected_date,
        'selected_doctor': doctor,
        'selected_daily_slot_status': selected_daily_slot_status,
    }

    return render(request, template_page, context=template_context)


def daily_slot_schedule_details(request, id):
    template_page = 'receptionist/daily_slot_schedule_details.html'

    change_daily_slot_status_form = ChangeDailySlotStatus()
    daily_slot_booking = DailySlotBooking.objects.filter(id=id).first()

    if request.method == 'POST':
        change_daily_slot_status_form = ChangeDailySlotStatus(request.POST)
        if change_daily_slot_status_form.is_valid():
            daily_slot_booking.status = change_daily_slot_status_form.cleaned_data[
                'daily_slot_status']
            daily_slot_booking.save()
            messages.success(request, 'Status updated successfully')
            # return redirect('receptionist:daily-slots-schedule')

    template_context = {
        'daily_slot_booking': daily_slot_booking,
        'change_daily_slot_status_form': change_daily_slot_status_form,
    }

    return render(request, template_page, context=template_context)


def get_day_from_date(date):
    return date.strftime("%A")


def generate_daily_slot_schedule(request):
    template_page = 'receptionist/generate_daily_slot_schedule.html'

    generate_daily_slot_schedule_form = GenerateDailySlotScheduleForm()

    generated_daily_schedule = DailySlotBooking.objects.none()

    if request.method == 'POST':
        generate_daily_slot_schedule_form = GenerateDailySlotScheduleForm(
            request.POST or None)

        if generate_daily_slot_schedule_form.is_valid():
            next_working_days = generate_daily_slot_schedule_form.cleaned_data[
                'next_working_days']
            doctors_list = generate_daily_slot_schedule_form.cleaned_data['doctors']
            for day in next_working_days:
                day_date = datetime.datetime.strptime(day, '%Y-%m-%d')
                for doctor in doctors_list:
                    doctor_user = doctor.user
                    doctor_time_slots = DoctorTimeSlot.objects.filter(doctor=doctor_user,
                                                                      time_slot__day=get_day_from_date(
                                                                          day_date),
                                                                      deleted=False).order_by('time_slot__start_time')
                    for doctor_time_slot in doctor_time_slots:
                        daily_slot_booking, created = DailySlotBooking.objects.get_or_create(
                            date=day_date,
                            doctor_time_slot=doctor_time_slot,
                            status='AVAILABLE'
                        )
                        generated_daily_schedule = generated_daily_schedule | DailySlotBooking.objects.filter(
                            id=daily_slot_booking.id)

            messages.success(request, 'Daily schedule generated successfully')

    template_context = {
        'generate_daily_slot_schedule_form': generate_daily_slot_schedule_form,
        'generated_daily_schedule': generated_daily_schedule,
    }

    return render(request, template_page, context=template_context)


def appointment_create(request):
    template_page = 'receptionist/appointment_create.html'

    create_new_appointment_form = CreateNewAppointmentForm()

    if request.method == 'POST':
        create_new_appointment_form = CreateNewAppointmentForm(
            request.POST or None)
        if create_new_appointment_form.is_valid():
            selected_date = create_new_appointment_form.cleaned_data['next_working_days']
            selected_doctor = create_new_appointment_form.cleaned_data['doctors']
            print(selected_date, selected_doctor)
            daily_slot_bookings = DailySlotBooking.objects.filter(
                date=selected_date,
                doctor_time_slot__doctor=selected_doctor.user,
                doctor_time_slot__time_slot__day=get_day_from_date(datetime.datetime.strptime(selected_date, '%Y-%m-%d')), deleted=False)
            print(daily_slot_bookings)
            half_times = daily_slot_bookings.values_list(
                'doctor_time_slot__time_slot__half_time',flat=True).distinct()
            template_context = {
                'create_new_appointment_form': create_new_appointment_form,
                'daily_slot_bookings': daily_slot_bookings,
                'half_times': half_times,
                'selected_date': selected_date,
                'selected_doctor': selected_doctor,
            }

            request.session['selected_date'] = selected_date

            return render(request, template_page, context=template_context)
            
    template_context = {
        'create_new_appointment_form': create_new_appointment_form,

    }

    return render(request, template_page, context=template_context)

def enter_patient_details(request):
    template_page = 'receptionist/enter_patient_details.html'

    patient_phone_no_form = PatientPhoneNoForm()
    patient_profile_form= EnterPatientprofileForm()
    patient_message_form= EnterPatientMessageForm()

    if request.method == 'POST':
        patient_phone_no_form = PatientPhoneNoForm(
            request.POST or None)
        patient_profile_form = EnterPatientprofileForm(
            request.POST or None)
        patient_message_form = EnterPatientMessageForm(
            request.POST or None)
        if patient_phone_no_form.is_valid() and patient_profile_form.is_valid() and patient_message_form.is_valid():
            patient_phone_no = patient_phone_no_form.cleaned_data['phone_no']
            patient_name = patient_profile_form.cleaned_data['name']
            patient_age = patient_profile_form.cleaned_data['age']
            

    template_context = {
        'patient_phone_no_form': patient_phone_no_form,
        'patient_profile_form': patient_profile_form,
        'patient_message_form': patient_message_form,
    }

    return render(request, template_page, context=template_context)

def book_slot(request):
    if request.method == "POST":
        selected_slot = request.POST.get("input_selected_slot")
        selected_date = request.session["selected_date"]
        print( selected_slot)
        request.session["selected_slot"] = selected_slot

        return redirect('receptionist:select-patient')
    return redirect('receptionist:create-appointment')

def patient_create(request):
    template_page = 'receptionist/patient_create.html'

    patient_phone_no_form = PatientPhoneNoForm()
    patient_profile_form= EnterPatientprofileForm()

    if request.method == 'POST':
        patient_phone_no_form = PatientPhoneNoForm(
            request.POST or None)
        patient_profile_form = EnterPatientprofileForm(
            request.POST or None)
        if patient_phone_no_form.is_valid() and patient_profile_form.is_valid():
            profile_data = {
                'first_name': patient_profile_form.cleaned_data['first_name'],
                'middle_name': patient_profile_form.cleaned_data['middle_name'],
                'last_name': patient_profile_form.cleaned_data['last_name'],
                'age': patient_profile_form.cleaned_data['age'],
                'address': patient_profile_form.cleaned_data['address'],
                'email': patient_profile_form.cleaned_data['email'],
                'gender': patient_profile_form.cleaned_data['gender'],
                'blood_group': patient_profile_form.cleaned_data['blood_group']

            }
            phone_no=patient_phone_no_form.cleaned_data['phone_no']
            patient = PatientRepository().create(data={"phone_no": phone_no})
            print(patient.patientprofile.first_name)
            PatientProfileRepository().update_by_patient(patient, profile_data)
            messages.success(request, 'Patient Created Successfully')
            
    
    template_context = {
        'patient_phone_no_form': patient_phone_no_form,
        'patient_profile_form': patient_profile_form,
    }
    return render(request, template_page, context=template_context)

def select_patient(request):
    template_page = 'receptionist/select_patient.html'
    patients_list = Patient.objects.all().distinct()

    selected_search_filters = request.GET.get('search-patients', None)
    if selected_search_filters:
        patients_list = patients_list.filter(
            Q(patientprofile__first_name__icontains=selected_search_filters) | Q(patientprofile__last_name__icontains=selected_search_filters) | Q(
                phone_no__icontains=selected_search_filters) | Q(patientprofile__address__icontains=selected_search_filters)
        )

    page = request.GET.get('page', 1)

    PAGE_OFFSET = 5
    paginator = Paginator(patients_list, PAGE_OFFSET)
    try:
        patients_arr = paginator.page(page)
    except PageNotAnInteger:
        patients_arr = paginator.page(1)
    except EmptyPage:
        patients_arr = paginator.page(paginator.num_pages)

    template_context = {
        'patients': patients_arr
    }

    return render(request, template_page, context=template_context)

def enter_patient_message(request,id):
    template_page = 'receptionist/enter_patient_message.html'

    patient_message_form= EnterPatientMessageForm()
    selected_patient=Patient.objects.filter(id=id).first()

    if request.method == 'POST':
        patient_message_form = EnterPatientMessageForm(
            request.POST or None)
        if patient_message_form.is_valid():
            message=patient_message_form.cleaned_data['message']    
            daily_slot_booking=DailySlotBooking.objects.filter(id=request.session["selected_slot"]).first()
            daily_slot_booking.status="BOOKED"
            daily_slot_booking.save()

            appointment,created= Appointment.objects.get_or_create(
                patient=selected_patient,
                daily_slot_booking=daily_slot_booking,
                message=message,
                status="PENDING"
            )
            return redirect('receptionist:appointment-details',
                            appointment.id)

    template_context = {
        'patient_message_form': patient_message_form,
        'selected_patient': selected_patient,
    }
    return render(request, template_page, context=template_context)

def generate_prescription_and_invoice(request,id):
    template_page = 'receptionist/generate_prescription_and_invoice.html'
    
    add_prescription_form= AddPrescriptionForm()
    generate_invoice_form= GenerateInvoiceForm()

    selected_appointment=Appointment.objects.filter(id=id).first()

    if selected_appointment.status=="COMPLETED":
        messages.error(request, 'Appointment Already Completed')
        return redirect('receptionist:appointment-details',
                            selected_appointment.id)

    if request.method == 'POST':
        add_prescription_form = AddPrescriptionForm(request.POST or None)
        generate_invoice_form = GenerateInvoiceForm(request.POST or None)
        if add_prescription_form.is_valid() and generate_invoice_form.is_valid():
            selected_appointment.status="COMPLETED"
            selected_appointment.save()

            prescription_content=add_prescription_form.cleaned_data['content']
            prescription_symptoms=add_prescription_form.cleaned_data['symptoms']

            prescription,created=Prescription.objects.get_or_create(
                appointment=selected_appointment,
                content=prescription_content,
                symptoms=prescription_symptoms
            )

            consultation_fee=generate_invoice_form.cleaned_data['consultation_fee']
            medicine_charges=generate_invoice_form.cleaned_data['medicine_charges']
            lab_fee=generate_invoice_form.cleaned_data['lab_fee']
            other_charges=generate_invoice_form.cleaned_data['other_charges']

            total_amount=consultation_fee+medicine_charges+lab_fee+other_charges
            
            invoice,created=Invoice.objects.get_or_create(
                appointment=selected_appointment,
                consultation_fee=consultation_fee,
                medicine_charges=medicine_charges,
                lab_fee=lab_fee,
                other_charges=other_charges,
                total_amount=total_amount,
                status="PAID")

            messages.success(request, 'Appointment Completed Successfully')
            return redirect('receptionist:prescription-and-invoice-details',
                            selected_appointment.id)

    template_context = {
        'add_prescription_form': add_prescription_form, 
        'generate_invoice_form': generate_invoice_form,
        'consultation_fee': selected_appointment.daily_slot_booking.doctor_time_slot.doctor.doctor.fees
    }

    return render(request, template_page, context=template_context)

def prescription_and_invoice_details(request,id):
    template_page = 'receptionist/prescription_and_invoice_details.html'
    selected_appointment=Appointment.objects.filter(id=id).first()
    prescription=Prescription.objects.filter(appointment=selected_appointment).first()
    invoice=Invoice.objects.filter(appointment=selected_appointment).first()

    template_context = {
        'selected_appointment': selected_appointment,
        'prescription': prescription,
        'invoice': invoice
    }


    return render(request, template_page, context=template_context)
   

