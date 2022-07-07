import datetime
from time import time
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from appointment.models import Appointment, DailySlotBooking
from patient.models import Patient

from .models import Doctor, DoctorTimeSlot, TimeSlot

from .forms import AddTimeSlotForm, DoctorUserForm, DoctorForm, EditDoctorForm, EditTimeSlotForm, GetTimeSlotForm, TimeSlotForm

# Create your views here.
USER_GROUP = {
    'DOCTOR': 'DOCTOR',
}


def home(request):
    return render(request, 'doctor/index.html')


def add_doctor(request):
    doctor_user_form = DoctorUserForm()
    doctor_form = DoctorForm()
    template_context = {
        'doctor_user_form': doctor_user_form,
        'doctor_form': doctor_form
    }
    if request.method == 'POST':
        doctor_user_form = DoctorUserForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)
        print(doctor_user_form.errors)
        print(doctor_form.errors)
        if doctor_user_form.is_valid() and doctor_form.is_valid():

            doctor_user = doctor_user_form.save()
            doctor_user.set_password(doctor_user.password)
            doctor_user.save()

            doctor = doctor_form.save(commit=False)
            doctor.user = doctor_user
            doctor = doctor.save()

            add_user_to_group(doctor_user, 'DOCTOR')

            return HttpResponse('Doctor added successfully')
    return render(request, 'doctor/add_doctor.html', context=template_context)


def add_user_to_group(user, group):
    group = Group.objects.get(name=USER_GROUP[group])
    group.user_set.add(user)


def add_time_slot(request):
    time_slot_form = TimeSlotForm()
    if request.method == 'POST':
        time_slot_form = TimeSlotForm(request.POST or None)
        if time_slot_form.is_valid():
            time_slot, created = TimeSlot.objects.get_or_create(
                day=time_slot_form.cleaned_data['day'],
                start_time=time_slot_form.cleaned_data['start_time'],
                end_time=time_slot_form.cleaned_data['end_time'],
                half_time=time_slot_form.cleaned_data['half_time']
            )
            # doctor_time_slot = DoctorTimeSlot.objects.filter(
            #     doctor=request.user, time_slot=time_slot)
            # if doctor_time_slot.exists():
            #     raise time_slot_form.ValidationError(
            #         "Time Slot already exists")

            doctor_time_slot, created = DoctorTimeSlot.objects.get_or_create(
                doctor=request.user,
                time_slot=time_slot
            )
            if created:
                messages.success(request, 'Time Slot added successfully')
                return render(request, 'doctor/add_time_slot.html', context={'time_slot_form': time_slot_form})
            else:
                time_slot_form.errors.update(
                    {'__all__': ['Time Slot already exists']})
    template_context = {'time_slot_form': time_slot_form}
    return render(request, 'doctor/add_time_slot.html', context=template_context)


def add_time_slots(request):
    time_slot_form = TimeSlotForm()
    if request.method == 'POST':
        time_slot_form = TimeSlotForm(request.POST or None)
        if time_slot_form.is_valid():
            time_slot, created = TimeSlot.objects.get_or_create(
                day=time_slot_form.cleaned_data['day'],
                start_time=time_slot_form.cleaned_data['start_time'],
                end_time=time_slot_form.cleaned_data['end_time'],
                half_time=time_slot_form.cleaned_data['half_time']
            )
            # doctor_time_slot = DoctorTimeSlot.objects.filter(
            #     doctor=request.user, time_slot=time_slot)
            # if doctor_time_slot.exists():
            #     raise time_slot_form.ValidationError(
            #         "Time Slot already exists")

            doctor_time_slot, created = DoctorTimeSlot.objects.get_or_create(
                doctor=request.user,
                time_slot=time_slot
            )
            if created:
                messages.success(request, 'Time Slot added successfully')
                return render(request, 'doctor/add_time_slots.html', context={'time_slot_form': time_slot_form})
            else:
                time_slot_form.errors.update(
                    {'__all__': ['Time Slot already exists']})
    template_context = {'time_slot_form': time_slot_form}
    return render(request, 'doctor/add_time_slots.html', context=template_context)


def get_today_day():
    return datetime.date.today().strftime('%A')


def time_slots(request):
    template_page = 'doctor/time_slots.html'

    get_time_slots_form = GetTimeSlotForm()

    page = request.GET.get('page', 1)
    selected_day = request.GET.get('days', get_today_day())
    if not selected_day:
        selected_day = get_today_day()

    # time_slots = DoctorTimeSlot.objects.filter(doctor=request.user, time_slot__day=get_today_day())
    # doctor_time_slots=DoctorTimeSlot.objects.all()
    doctor_time_slots = DoctorTimeSlot.objects.filter(
        doctor=request.user, time_slot__day=selected_day, time_slot__deleted=False)

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
        'selected_day': selected_day
    }

    return render(request, template_page, context=template_context)


def edit_time_slot(request, id):
    template_page = 'doctor/edit_time_slot.html'
    time_slot = TimeSlot.objects.filter(id=id).first()
    edit_time_slot_form = EditTimeSlotForm(instance=time_slot)
    if request.method == 'POST':
        edit_time_slot_form = EditTimeSlotForm(request.POST or None)
        if edit_time_slot_form.is_valid():
            day = edit_time_slot_form.cleaned_data['day']
            start_time = edit_time_slot_form.cleaned_data['start_time']
            end_time = edit_time_slot_form.cleaned_data['end_time']
            time_slot.day = day
            time_slot.start_time = start_time
            time_slot.end_time = end_time
            time_slot.save()
            messages.success(request, 'Time Slot updated successfully')
    template_context = {
        'edit_time_slot_form': edit_time_slot_form,
        'time_slot_id': id
    }
    return render(request, template_page, context=template_context)


def delete_time_slot(request, id):
    time_slot = TimeSlot.objects.filter(id=id).first()
    time_slot.deleted = True
    time_slot.save()
    doctor_time_slot = DoctorTimeSlot.objects.filter(
        doctor=request.user, time_slot=time_slot).first()
    doctor_time_slot.deleted = True
    doctor_time_slot.save()
    daily_slot_bookings = DailySlotBooking.objects.filter(
        doctor_time_slot=doctor_time_slot, status="AVAILABLE")
    daily_slot_bookings.update(deleted=True)
    print(daily_slot_bookings)

    messages.success(request, 'Time Slot deleted successfully')
    return redirect('doctor:time-slots')


def get_session_from_time(time):
    if time.hour < 12:
        return "Morning"
    elif time.hour < 16:
        return "Afternoon"
    else:
        return "Evening"


def add_time_slot(request):
    template_page = 'doctor/add_time_slots.html'
    add_time_slot_form = AddTimeSlotForm()
    if request.method == 'POST':
        add_time_slot_form = AddTimeSlotForm(request.POST or None)
        if add_time_slot_form.is_valid():
            days = add_time_slot_form.cleaned_data['days']
            start_time = add_time_slot_form.cleaned_data['start_time']
            end_time = add_time_slot_form.cleaned_data['end_time']
            print(start_time.hour)
            no_of_slots_created = 0
            for day in days:
                time_slot, created = TimeSlot.objects.update_or_create(
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    half_time=get_session_from_time(start_time)
                )
                doctor_time_slot, created = DoctorTimeSlot.objects.get_or_create(
                    doctor=request.user,
                    time_slot=time_slot
                )
                if created:
                    no_of_slots_created += 1

            if no_of_slots_created > 0:
                messages.success(request, 'Time Slot added successfully')
                return redirect('doctor:time-slots')
            else:
                add_time_slot_form.errors.update(
                    {'__all__': ['Time Slot already exists']})
                template_context = {'add_time_slot_form': add_time_slot_form}
                return render(request, template_page, context=template_context)
           
    template_context = {
        'add_time_slot_form': add_time_slot_form
    }

    return render(request, template_page, context=template_context)

def my_appointments(request):
    template_page = 'doctor/my_appointments.html'
    my_appointments = Appointment.objects.filter(
        daily_slot_booking__doctor_time_slot__doctor=request.user,
    )

    page = request.GET.get('page', 1)

    PAGE_OFFSET = 5
    paginator = Paginator(my_appointments, PAGE_OFFSET)
    try:
        appointments = paginator.page(page)
    except PageNotAnInteger:
        appointments = paginator.page(1)
    except EmptyPage:
        appointments = paginator.page(paginator.num_pages)


    template_context = {
        'my_appointments': appointments
    }
    return render(request, template_page, context=template_context)

def appointment_details(request, id):
    template_page = 'doctor/appointment_details.html'
    appointment = Appointment.objects.filter(id=id).first()
    template_context = {
        'appointment': appointment
    }
    return render(request, template_page, context=template_context)


def my_patients(request):
    template_page = 'doctor/my_patients.html'

    # Get all patients who have booked an appointment with this doctor
    my_appointments = Appointment.objects.filter(
        daily_slot_booking__doctor_time_slot__doctor=request.user,
    )
    my_patients = my_appointments.values_list('patient', flat=True).distinct()
    my_patients = Patient.objects.filter(id__in=my_patients)

    page = request.GET.get('page', 1)

    PAGE_OFFSET = 5
    paginator = Paginator(my_patients, PAGE_OFFSET)
    try:
        patients = paginator.page(page)
    except PageNotAnInteger:
        patients = paginator.page(1)
    except EmptyPage:
        patients = paginator.page(paginator.num_pages)

    template_context = {
        'patients': patients
    }
    return render(request, template_page, context=template_context)

def patient_details(request, id):
    template_page = 'doctor/patient_details.html'
    patient = Patient.objects.filter(id=id).first()
    template_context = {
        'patient': patient
    }
    return render(request, template_page, context=template_context)


def doctor_profile(request):
    template_page = 'doctor/doctor_profile.html'
    doctor = request.user
    doctor_profile_form = EditDoctorForm(instance=doctor.doctor)

    if request.method == 'POST':
        doctor_profile_form = EditDoctorForm(request.POST, instance=doctor.doctor)
        if doctor_profile_form.is_valid():

            data={
                'first_name': doctor_profile_form.cleaned_data['first_name'],
                'middle_name': doctor_profile_form.cleaned_data['middle_name'],
                'last_name': doctor_profile_form.cleaned_data['last_name'],
                
                'phone_no': doctor_profile_form.cleaned_data['phone_no'],
                'address': doctor_profile_form.cleaned_data['address'],

                'specialization': doctor_profile_form.cleaned_data['specialization'],
                'qualification': doctor_profile_form.cleaned_data['qualification'],
                'experience': doctor_profile_form.cleaned_data['experience'],

                'fees': doctor_profile_form.cleaned_data['fees'],
                'timings': doctor_profile_form.cleaned_data['timings'],

                'profile_image': doctor_profile_form.cleaned_data['profile_image'],
                'certificate_image': doctor_profile_form.cleaned_data['certificate_image'],
            }
            
            doctor_profile_obj=doctor_profile_form.save(commit=False)
            if 'profile_image' in request.FILES:
                doctor_profile_obj.profile_image = request.FILES['profile_image']
            if 'certificate_image' in request.FILES:
                doctor_profile_obj.certificate_image = request.FILES['certificate_image']
            doctor_profile_obj.save()
            # if request.FILES:
            #     data['profile_image'] = request.FILES['profile_image']
            #     data['certificate_image'] = request.FILES['certificate_image']

            # print(request.FILES)
            # doctor_found= Doctor.objects.filter(user=doctor)
            # doctor_found.update(**data)
            # doctor_found.profile_image = request.FILES['profile_image']
            # doctor_found.certificate_image = request.FILES['certificate_image']
            # doctor_found.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('doctor:doctor-profile')
            # print(doctor_profile_form.cleaned_data)

    template_context = {
        'doctor': doctor,
        'doctor_profile_form': doctor_profile_form
    }
    return render(request, template_page, context=template_context)