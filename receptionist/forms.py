from django import forms
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import datetime
from phonenumber_field.formfields import PhoneNumberField

from doctor.models import Doctor
from appointment.models import Invoice, Prescription
from patient.models import PatientProfile,Patient

from .models import Receptionist

User = get_user_model()


class ReceptionistUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class ReceptionistForm(forms.ModelForm):
    class Meta:
        model = Receptionist
        fields = ['first_name', 'middle_name',
                  'last_name', 'phone_no', 'address', 'profile_image']


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class DailyBookingForm(forms.Form):
    doctor_choices = Doctor.objects.all().values_list('id', 'first_name')
    # date = forms.DateField(initial=date.today(),
    #                        widget=forms.DateInput(attrs={'type': 'date'}))
    # doctors = forms.MultipleChoiceField(
    #     choices=doctor_choices, widget=forms.CheckboxSelectMultiple())
    doctors = CustomModelMultipleChoiceField(label="Select Doctors", queryset=Doctor.objects.all(), initial=list(Doctor.objects.all()), widget=forms.CheckboxSelectMultiple())

DAY_CHOICES = (('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
               ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'))


def get_today_day():
    import datetime
    today = datetime.datetime.now()
    return f'{today.strftime("%A")}'

class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class GetTimeSlotForm(forms.Form):
    days = forms.ChoiceField(choices=DAY_CHOICES, widget=forms.RadioSelect(
        attrs={'class': 'form-control'},
    ), initial=get_today_day
    )
    doctors = CustomModelChoiceField(label="Select Doctor", queryset=Doctor.objects.all(
    ), initial=Doctor.objects.first(), widget=forms.RadioSelect)


def get_next_working_day(date):
    return date + timedelta(days=1) if date.weekday() == 6 else date


class CustomDateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        # kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)

APPOINTMENT_STATUS_CHOICES = (('ALL', 'All'),('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'))

class GetAppointmentsForm(forms.Form):
    date = forms.DateField(widget=CustomDateInput(
        format=["%Y-%m-%d"], attrs={
            # 'min': get_next_working_day(datetime.datetime.now().date()).strftime("%Y-%m-%d"),
            'max': get_next_working_day((datetime.datetime.now() + timedelta(days=7)).date()).strftime("%Y-%m-%d"),
        }),required=False, label="Select Date")
    
    appointment_status=forms.ChoiceField(choices=APPOINTMENT_STATUS_CHOICES, widget=forms.RadioSelect(
        attrs={'class': 'form-control'},
    ), error_messages={
            'required': 'Please select status',
    })

class GetPatientsForm(forms.Form):
    doctors = CustomModelChoiceField(label="Select Doctor", queryset=Doctor.objects.all(
    ), initial=Doctor.objects.first(), widget=forms.RadioSelect)


class EditReceptionistForm(forms.ModelForm):
    class Meta:
        model = Receptionist
        fields = ['first_name', 'middle_name',
                  'last_name', 'phone_no', 'address',  'profile_image', ]

DAILY_SLOT_STATUS_CHOICES = (('BOOKED', 'Booked'),('AVAILABLE', 'Available'), ('NOT-AVAILABLE', 'Not Available'))

class DailySlotScheduleForm(forms.Form):
    date = forms.DateField(widget=CustomDateInput(
        format=["%Y-%m-%d"], attrs={
            # 'min': get_next_working_day(datetime.datetime.now().date()).strftime("%Y-%m-%d"),
            'max': get_next_working_day((datetime.datetime.now() + timedelta(days=7)).date()).strftime("%Y-%m-%d"),
        }),required=False, label="Select Date")
    
    doctors = CustomModelChoiceField(label="Select Doctor", queryset=Doctor.objects.all(
    ), initial=Doctor.objects.first(), widget=forms.RadioSelect)
   
    daily_slot_status=forms.ChoiceField(choices=DAILY_SLOT_STATUS_CHOICES, widget=forms.RadioSelect(
        attrs={'class': 'form-control'},
    ), error_messages={
            'required': 'Please select status',
    })

class ChangeDailySlotStatus(forms.Form):
    daily_slot_status=forms.ChoiceField(choices=DAILY_SLOT_STATUS_CHOICES, widget=forms.RadioSelect(
        attrs={'class': 'form-control'},
    ), error_messages={
            'required': 'Please select status',
    })


def get_next_working_day(input_date):
    if input_date.weekday() == 6:
        return input_date + timedelta(days=1)
    else:
        return input_date

def get_n_working_days(n):
   
    today = datetime.date.today()
    next_working_days = []
    for i in range(n):
        next_day = today + datetime.timedelta(days=i)
        d= get_next_working_day(next_day)
        if d in next_working_days:
            nd=get_next_working_day(d+datetime.timedelta(days=1))
            next_working_days.append(nd)
        if d not in next_working_days:
            next_working_days.append(d)
    return next_working_days


def get_next_working_days_choices_tuple():
    next_working_days = get_n_working_days(7)
    return tuple((str(d), d) for d in next_working_days)

class GenerateDailySlotScheduleForm(forms.Form):
    # next_working_days=forms.MultipleChoiceField(choices=get_next_working_days_choices_tuple(), widget=forms.CheckboxSelectMultiple(
    #     attrs={'class': 'form-control'},
    # ), initial=get_next_working_day(datetime.datetime.now().date()).strftime("%Y-%m-%d"), required=False
    # )
    next_working_days=forms.MultipleChoiceField(choices=get_next_working_days_choices_tuple, widget=forms.CheckboxSelectMultiple(
       
    ), required=False)
    doctors = CustomModelMultipleChoiceField(label="Select Doctors", queryset=Doctor.objects.all(), initial=list(Doctor.objects.all()), widget=forms.CheckboxSelectMultiple(), required=False)

class CreateNewAppointmentForm(forms.Form):
    next_working_days=forms.ChoiceField(choices=get_next_working_days_choices_tuple, widget=forms.RadioSelect(
       
    ), required=False)
    doctors = CustomModelChoiceField(label="Select Doctors", queryset=Doctor.objects.all(), initial=list(Doctor.objects.all()), widget=forms.RadioSelect(), required=False)

class PatientPhoneNoForm(forms.Form):
    phone_no = PhoneNumberField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': ('Phone'), 'pattern': '[789][0-9]{9}'}))

GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'))
BLOOD_GROUP_CHOICES = (('AB+', 'AB+'), ('AB-', 'AB-'), ('A+', 'A+'),
                       ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'))

class EnterPatientprofileForm(forms.ModelForm):
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)

    class Meta:
        model = PatientProfile
        fields = ['first_name', 'middle_name',
                  'last_name', 'age', 'address', 'email', 'gender', 'blood_group']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ram'
                    
                },
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Charan'
                },
            ),
            'middle_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Raju'
                },
            ),
            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '30'}
            ),
            'address': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Sector-1, Gurgaon'
            }),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'asdf@gmail.com'
                }
            ),
            'gender': forms.RadioSelect(choices=GENDER_CHOICES),

        }
    
class EnterPatientPhoneNoForm(forms.Form):
    phone_no = PhoneNumberField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': ('Phone'), 'pattern': '[789][0-9]{9}'}))

class EnterPatientMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': ('Your message'),'rows':4}),       label=("Your message"))
    

class AddPrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields =['content','symptoms',]

        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Prescription by doctor goes here'
            }),
            'symptoms': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Symptoms goes here'
            }),
        }
        
class GenerateInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['consultation_fee','medicine_charges','lab_fee','other_charges','total_amount']

        widgets = {
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Consultation fee',
                'value': '0',
                'pattern': '[0-9]*',
            }),
            'medicine_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medicine charges',
                'value': '0',
                'pattern': '[0-9]*'
            }),
            'lab_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lab fee',
                'value': '0',
                'pattern': '[0-9]*'
            }),
            'other_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Other charges',
                'value': '0',
                'pattern': '[0-9]*'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total amount',
                'pattern': '[0-9]*'
                
            }),
            
        }
        
