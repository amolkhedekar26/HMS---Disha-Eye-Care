from datetime import date, datetime
import json
from re import template
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.forms.utils import ErrorList

from appointment.models import Appointment, DailySlotBooking, Invoice, Prescription
from doctor.models import Doctor

from receptionist.forms import DailyBookingForm, User

from .forms import ChooseDateForm, GetOTPForm, PatientMessageForm, PatientProfileForm, VerifyOTPForm

from .repositories.patient_profile import PatientProfileRepository

from .repositories.patient import PatientRepository

from .models import OTP

from .services.fast2sms import Fast2SMS
from .services.py_otp import TOTP

# Create your views here.


def home(request):
    return render(request, 'patient/index.html')

def save_patient_profile(request):
    if request.method == "POST":
        input_first_name = request.POST.get("input-first-name")
        input_middle_name = request.POST.get("input-middle-name")
        input_last_name = request.POST.get("input-last-name")
        input_age = request.POST.get("input-age")
        input_address = request.POST.get("input-address")
        input_email = request.POST.get("input-email")
        input_gender = request.POST.get("input-gender")
        input_blood_group = request.POST.get("input-blood-group")
        print(input_gender)
        data = {
            "first_name": input_first_name,
            "middle_name": input_middle_name,
            "last_name": input_last_name,
            "age": input_age,
            "address": input_address,
            "email": input_email,
            "gender": input_gender,
            "blood_group": input_blood_group

        }
        input_phone_no = request.session["phone_no"]
        patient = PatientRepository().get_by_phone_no(
            phone_no=input_phone_no)
        PatientProfileRepository().update_by_patient(patient, data)
        return HttpResponse("Go to next page")
    return render(request, 'patient/patient_profile.html')


def get_day_from_date(date):
    return date.strftime("%A")


def check_slot_availability(request):
    choose_date_form = ChooseDateForm()
    if request.method == "POST":
        choose_date_form = ChooseDateForm(request.POST or None)
        if choose_date_form.is_valid():
            selected_date = choose_date_form.cleaned_data['date']
            doctor = choose_date_form.cleaned_data['doctor']

            daily_slot_bookings = DailySlotBooking.objects.filter(
                date=selected_date)
            print(get_day_from_date(selected_date))
            slots_available = []
            for daily_slot_booking in daily_slot_bookings:
                if daily_slot_booking.doctor_time_slot.time_slot.day == get_day_from_date(selected_date) and daily_slot_booking.doctor_time_slot.doctor == doctor.user:
                    # if daily_slot_booking.status == "AVAILABLE":
                    #     slots_available.append(
                    #         daily_slot_booking)
                    slots_available.append(daily_slot_booking)
            print(slots_available)
            template_context = {
                "choose_date_form": choose_date_form,
                "slots_available": slots_available,
                "selected_date": selected_date,
                "doctor": doctor}
            request.session["selected_date"] = selected_date.strftime(
                "%Y-%m-%d")
            return render(request, 'patient/check_slot_availability.html',
                          context=template_context)

    template_context = {
        "choose_date_form": choose_date_form
    }
    return render(request, 'patient/check_slot_availability.html', context=template_context)


def book_slot(request):
    if request.method == "POST":
        selected_slot = request.POST.get("input_selected_slot")
        selected_date = request.session["selected_date"]
        print(selected_date, selected_slot)
        request.session["selected_slot"] = selected_slot

        # daily_booking_slot = DailySlotBooking.objects.get(id=selected_slot)
        # daily_booking_slot.status = "BOOKED"
        # daily_booking_slot.save()
        # return HttpResponse(f"Booked {daily_booking_slot}")
        return redirect('patient:get-otp')
    return render(request, 'patient/check_available_slot.html')


def get_doctors_for_day(request):
    selected_day = request.GET.get("selected_day")
    daily_slot_bookings = DailySlotBooking.objects.filter(date=selected_day)
    print(daily_slot_bookings)
    doctors = list(daily_slot_bookings.values_list(
        'doctor_time_slot__doctor', flat=True).distinct())
    print(doctors)
    available_doctors = Doctor.objects.filter(user__id__in=doctors)
    print(available_doctors)
    return HttpResponse(json.dumps({'doctors': list(available_doctors.values())}))


def get_available_slots(request):
    choose_date_form = ChooseDateForm(request.POST or None)
    selected_date = request.POST.get("date")
    selected_doctor = request.POST.get("doctor-select")
    print(selected_date, selected_doctor)
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
    doctor = Doctor.objects.get(id=selected_doctor)
    daily_slot_bookings = DailySlotBooking.objects.filter(
        date=selected_date)
    print(get_day_from_date(selected_date))
    slots_available = []
    slots = daily_slot_bookings.filter(doctor_time_slot__time_slot__day=get_day_from_date(
        selected_date), doctor_time_slot__doctor=doctor.user)
    print(slots)
    # for daily_slot_booking in daily_slot_bookings:
    #     if daily_slot_booking.doctor_time_slot.time_slot.day == get_day_from_date(selected_date) and daily_slot_booking.doctor_time_slot.doctor == doctor.user:
    #         # if daily_slot_booking.status == "AVAILABLE":
    #         #     slots_available.append(
    #         #         daily_slot_booking)
    #         slots_available.append(daily_slot_booking)
    # print(slots_available)
    # template_context = {
    #     "slots_available": slots,
    #     "selected_date": selected_date,
    #     "doctor": doctor}
    # request.session["selected_date"] = selected_date.strftime(
    #     "%Y-%m-%d")
    # return render(request, 'patient/check_slot_availability.html',
    #               context=template_context)

    return HttpResponse(json.dumps({'slots': list(slots.values())}, indent=4, sort_keys=True, default=str))


def check_available_slots(request):
    template_page = 'patient/check_available_slot.html'
    choose_date_form = ChooseDateForm()

    if request.method == "POST":
        choose_date_form = ChooseDateForm(request.POST or None)
        if choose_date_form.is_valid():
            selected_date = choose_date_form.cleaned_data['date']
            doctor = choose_date_form.cleaned_data['doctor']

            daily_slot_bookings = DailySlotBooking.objects.filter(
                date=selected_date,deleted=False)
            print(get_day_from_date(selected_date))
            slots_available = []
            for daily_slot_booking in daily_slot_bookings:
                if daily_slot_booking.doctor_time_slot.time_slot.day == get_day_from_date(selected_date) and daily_slot_booking.doctor_time_slot.doctor == doctor.user:
                    # if daily_slot_booking.status == "AVAILABLE":
                    #     slots_available.append(
                    #         daily_slot_booking)
                    slots_available.append(daily_slot_booking)
            print(slots_available)
            template_context = {
                "choose_date_form": choose_date_form,
                "slots_available": slots_available,
                "selected_date": selected_date,
                "doctor": doctor}
            request.session["selected_date"] = selected_date.strftime(
                "%Y-%m-%d")
            return render(request, 'patient/check_available_slot.html',
                          context=template_context)

    template_context = {
        "choose_date_form": choose_date_form
    }
    return render(request, template_page, context=template_context)

def get_day_from_date(date):
    return date.strftime("%A")

def check_available_slots_new(request):
    template_page = 'patient/check_available_slot.html'
    choose_date_form = ChooseDateForm()

    if request.method == "POST":
        choose_date_form = ChooseDateForm(request.POST or None)
        if choose_date_form.is_valid():
            selected_date = choose_date_form.cleaned_data['date']
            doctor = choose_date_form.cleaned_data['doctor']
            print(selected_date, doctor)

            slots_available = DailySlotBooking.objects.filter(
                date=selected_date,
                doctor_time_slot__doctor=doctor.user,
                doctor_time_slot__time_slot__day=get_day_from_date(selected_date), deleted=False)
            print(slots_available)
            half_times = slots_available.values_list(
                'doctor_time_slot__time_slot__half_time',flat=True).distinct()

            # daily_slot_bookings = DailySlotBooking.objects.filter(
            #     date=selected_date,deleted=False)
            # print(get_day_from_date(selected_date))
            # slots_available = []
            # for daily_slot_booking in daily_slot_bookings:
            #     if daily_slot_booking.doctor_time_slot.time_slot.day == get_day_from_date(selected_date) and daily_slot_booking.doctor_time_slot.doctor == doctor.user:
            #         # if daily_slot_booking.status == "AVAILABLE":
            #         #     slots_available.append(
            #         #         daily_slot_booking)
            #         slots_available.append(daily_slot_booking)
            # print(slots_available)
            template_context = {
                "choose_date_form": choose_date_form,
                "slots_available": slots_available,
                'half_times': half_times,
                "selected_date": selected_date,
                "doctor": doctor,
                "active_tab": "check_available_slot_tab"}
            request.session["selected_date"] = selected_date.strftime(
                "%Y-%m-%d")
            return render(request, 'patient/check_available_slot.html',
                          context=template_context)

    template_context = {
        "choose_date_form": choose_date_form
    }
    return render(request, template_page, context=template_context)

def resend_otp(request):
    if request.method == "POST":
        input_phone_no=request.session["phone_no"]
        last_otp=OTP.objects.filter(phone_no=input_phone_no).order_by('-created_at').first()
        print(last_otp)
        if last_otp.is_expired:
            
            input_phone_no=request.session["phone_no"]
            totp = TOTP.generate_TOTP()
            OTP.objects.create(phone_no=input_phone_no,
                            secret=totp['secret'], otp=totp['otp'])
            
            # Fast2SMS.send_sms(str(input_phone_no)[3:], message)
            # set messesge to be sent to user
            messages.success(request, "OTP has been re-sent to your phone number")
            return redirect('patient:verify-otp')
        else:
            # set form errors
            messages.error(request, "Please wait for specified time to resend OTP i.e. 5 minutes")
            return redirect('patient:verify-otp')

def resend_otp_appointment_history(request):
    if request.method == "POST":
        input_phone_no=request.session["phone_no"]
        last_otp=OTP.objects.filter(phone_no=input_phone_no).order_by('-created_at').first()
        print(last_otp)
        if last_otp.is_expired:
            
            input_phone_no=request.session["phone_no"]
            totp = TOTP.generate_TOTP()
            OTP.objects.create(phone_no=input_phone_no,
                            secret=totp['secret'], otp=totp['otp'])
            
            # Fast2SMS.send_sms(str(input_phone_no)[3:], message)
            # set messesge to be sent to user
            messages.success(request, "OTP has been re-sent to your phone number")
            return redirect('patient:appointment-history-verify-otp')
        else:
            # set form errors
            messages.error(request, "Please wait for specified time to resend OTP i.e. 5 minutes")
            return redirect('patient:appointment-history-verify-otp')



def get_otp(request):
    template_page = 'patient/get_otp.html'
    get_otp_form = GetOTPForm()
    if request.method == "POST":
        get_otp_form = GetOTPForm(request.POST or None)
        if get_otp_form.is_valid():
            input_phone_no = get_otp_form.cleaned_data['phone_no']
            print(str(input_phone_no)[3:])
            request.session["phone_no"] = str(input_phone_no)
            totp = TOTP.generate_TOTP()
            OTP.objects.create(phone_no=input_phone_no,
                               secret=totp['secret'], otp=totp['otp'])
            message = f"Your One Time Password for booking an appointment  is {totp['otp']}. Please do not share this OTP with anyone. This OTP is valid for 5 minutes. Thank you."
            # Fast2SMS.send_sms(str(input_phone_no)[3:], message)
            return redirect('patient:verify-otp')

    template_context = {
        "get_otp_form": get_otp_form
    }
    return render(request, template_page, context=template_context)


def verify_otp(request):
    template_page = 'patient/verify_otp.html'
    verify_otp_form = VerifyOTPForm()
    if request.method == "POST":
        verify_otp_form = VerifyOTPForm(request.POST or None)
        if verify_otp_form.is_valid():
            # input_phone_no = request.POST.get("input-phone-no")
            input_phone_no = request.session["phone_no"]
            input_otp = verify_otp_form.cleaned_data['otp']
            # input_otp = request.POST.get("input-otp")
            otp = OTP.objects.filter(phone_no=input_phone_no).last()
            print(otp)
            if otp:
                # if otp.otp == input_otp:
                #     return render(request, 'patient/verify_otp.html')
                # else:
                #     return render(request, 'patient/enter_otp.html')
                if TOTP.verify_TOTP(otp.secret, input_otp):
                    # PatientRepository().create(
                    #     data={"phone_no": input_phone_no})
                    # return render(request, 'patient/patient_profile.html')
                    request.session["is_verified"] = True
                    request.session["verified_phone_no"] = input_phone_no
                    return redirect('patient:patient-profile')
                else:
                    errors = verify_otp_form._errors.setdefault("otp", ErrorList())
                    # errors.append(u"Invalid OTP. Please try again.")
                    # verify_otp_form.errors.update(
                    # {'__all__': ['Phone no and OTP do not match.']})
                    if "is_verified" in request.session:
                        del request.session["is_verified"]
                    if "verified_phone_no" in request.session:
                        del request.session["verified_phone_no"]

                    if "is_appointment_history_verified" in request.session:
                        del request.session["is_appointment_history_verified"]
                    if "appointment_history_verified_phone_no" in request.session:
                        del request.session["appointment_history_verified_phone_no"]
                    messages.error(request, "Invalid OTP. Please try again.")
                    template_context={
                        "verify_otp_form": verify_otp_form
                    }
                    return render(request, template_page, context=template_context)
                    # return render(request, 'patient/patient_profile.html')
            else:
                return HttpResponse("No OTP found")

    template_context = {
        "verify_otp_form": verify_otp_form
    }
    # return HttpResponse(TOTP.verify_TOTP(otp.secret, input_otp))
    return render(request, template_page, context=template_context)


def patient_profile(request):
    template_page = 'patient/patient_profile.html'

    phone_no = request.session["phone_no"]

    patient = PatientRepository().get_by_phone_no(phone_no)
    patient_profile_data = PatientProfileRepository().get_by_patient(patient)
    # print(patient_profile_data.first_name)
    if patient:
        patient_profile_form = PatientProfileForm(
            instance=patient_profile_data)
        response_messages = {
            'existing_patient': True,
            'patient_profile_data': patient_profile_data
        }
    else:
        patient_profile_form = PatientProfileForm()
        response_messages = {
            'existing_patient': False,
        }
    patient_message_form = PatientMessageForm()
    if request.method == "POST":
        patient_profile_form = PatientProfileForm(request.POST or None)
        patient_message_form = PatientMessageForm(request.POST or None)
        if patient_profile_form.is_valid() and patient_message_form.is_valid():
            data = {
                'first_name': patient_profile_form.cleaned_data['first_name'],
                'middle_name': patient_profile_form.cleaned_data['middle_name'],
                'last_name': patient_profile_form.cleaned_data['last_name'],
                'age': patient_profile_form.cleaned_data['age'],
                'address': patient_profile_form.cleaned_data['address'],
                'email': patient_profile_form.cleaned_data['email'],
                'gender': patient_profile_form.cleaned_data['gender'],
                'blood_group': patient_profile_form.cleaned_data['blood_group']

            }
            # patient_profile_form.save()
            phone_no = request.session["phone_no"]
            patient = PatientRepository().create(data={"phone_no": phone_no})
            print(patient)
            PatientProfileRepository().update_by_patient(patient, data)

            message = patient_message_form.cleaned_data['message']
            selected_slot = request.session["selected_slot"]

            daily_slot_booking = DailySlotBooking.objects.get(id=selected_slot)
            if daily_slot_booking.status != "BOOKED":
                daily_slot_booking.status = "BOOKED"
                daily_slot_booking.save()

                appointment = Appointment.objects.create(
                    patient=patient,
                    daily_slot_booking=daily_slot_booking,
                    message=message,
                    status="PENDING")

                # return render(request, 'patient/patient_profile.html')
                return redirect(reverse('patient:appointment-details', kwargs={'appointment_id': appointment.id}))
            else:
                return HttpResponse("Slot already booked")
            # return redirect('patient:patient-message')

    template_context = {
        "patient_profile_form": patient_profile_form,
        "patient_message_form": patient_message_form,
        "response_messages": response_messages
    }
    return render(request, template_page, context=template_context)


def appointment_details(request, appointment_id):
    template_page = 'patient/appointment_details.html'
    appointment = Appointment.objects.filter(id=appointment_id).last()
    if appointment:
        prescription=Prescription.objects.filter(appointment=appointment).last()
        invoice=Invoice.objects.filter(appointment=appointment).last()
        template_context = {
            "appointment": appointment,
            "prescription": prescription,
            "invoice": invoice
        }
    return render(request, template_page, context=template_context)


def patient_message(request):
    template_page = 'patient/patient_message.html'
    patient_message_form = PatientMessageForm()

    template_context = {
        "patient_message_form": patient_message_form
    }
    return render(request, template_page, context=template_context)


def appointment_history_get_otp(request):
    template_page = 'patient/appointment_history_get_otp.html'
    get_otp_form = GetOTPForm()
    if request.method == "POST":
        get_otp_form = GetOTPForm(request.POST or None)
        if get_otp_form.is_valid():
            input_phone_no = get_otp_form.cleaned_data['phone_no']
            print(str(input_phone_no)[3:])
            request.session["phone_no"] = str(input_phone_no)
            totp = TOTP.generate_TOTP()
            OTP.objects.create(phone_no=input_phone_no,
                               secret=totp['secret'], otp=totp['otp'])
            message = f"Your One Time Password for booking an appointment  is {totp['otp']}. Please do not share this OTP with anyone. This OTP is valid for 5 minutes. Thank you."
            # Fast2SMS.send_sms(str(input_phone_no)[3:], message)
            return redirect('patient:appointment-history-verify-otp')

    template_context = {
        "get_otp_form": get_otp_form
    }
    return render(request, template_page, context=template_context)


def appointment_history_verify_otp(request):
    template_page = 'patient/appointment_history_verify_otp.html'
    verify_otp_form = VerifyOTPForm()
    if request.method == "POST":
        verify_otp_form = VerifyOTPForm(request.POST or None)
        if verify_otp_form.is_valid():
            # input_phone_no = request.POST.get("input-phone-no")
            input_phone_no = request.session["phone_no"]
            input_otp = verify_otp_form.cleaned_data['otp']
            # input_otp = request.POST.get("input-otp")
            otp = OTP.objects.filter(phone_no=input_phone_no).last()
            print(otp)
            if otp:
                # if otp.otp == input_otp:
                #     return render(request, 'patient/verify_otp.html')
                # else:
                #     return render(request, 'patient/enter_otp.html')
                if TOTP.verify_TOTP(otp.secret, input_otp):
                    
                    request.session["is_appointment_history_verified"] = True
                    request.session["appointment_history_verified_phone_no"] = input_phone_no
                    return redirect('patient:appointment-history')
                else:
                    errors = verify_otp_form._errors.setdefault("otp", ErrorList())
                    # errors.append(u"Invalid OTP. Please try again.")
                    if "is_appointment_history_verified" in request.session:
                        del request.session["is_appointment_history_verified"]
                    if "appointment_history_verified_phone_no" in request.session:
                        del request.session["appointment_history_verified_phone_no"]
                    template_context = {
                        "verify_otp_form": verify_otp_form
                    }
                    messages.error(request, "Invalid OTP. Please try again.")
                    return render(request, template_page, context=template_context)
                    # return HttpResponse("Not Verified")
                    # return render(request, 'patient/patient_profile.html')
            else:
                return HttpResponse("No OTP found")

    template_context = {
        "verify_otp_form": verify_otp_form
    }
    return render(request, template_page, context=template_context)


def appointment_history(request):
    template_page = 'patient/appointment_history.html'

    if "is_verified" in request.session and request.session["is_verified"]:
        phone_no = request.session["verified_phone_no"]
        patient=PatientRepository().get_by_phone_no(phone_no)
        patient_profile_data=PatientProfileRepository().get_by_patient(patient)
        appointments = Appointment.objects.filter(patient__phone_no=phone_no).order_by('-id')
        template_context = {
            "appointments": appointments,
            "patient_profile_data": patient_profile_data
        }
        return render(request, template_page, context=template_context)

    elif "is_appointment_history_verified" in request.session and request.session["is_appointment_history_verified"]:
        phone_no = request.session["appointment_history_verified_phone_no"]
        patient=PatientRepository().get_by_phone_no(phone_no)
        patient_profile_data=PatientProfileRepository().get_by_patient(patient)
        appointments = Appointment.objects.filter(patient__phone_no=phone_no).order_by('-id')
        template_context = {
            "appointments": appointments,
            "patient_profile_data": patient_profile_data
        }
        return render(request, template_page, context=template_context)

    else:
        return redirect('patient:appointment-history-get-otp')

def appointment_home(request):
    template_page = 'patient/appointment_home.html'
    return render(request, template_page)