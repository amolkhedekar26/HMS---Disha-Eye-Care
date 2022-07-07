from datetime import timedelta
import datetime
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from doctor.models import Doctor
from .models import PatientProfile


def get_next_working_day(date):
    return date + timedelta(days=1) if date.weekday() == 6 else date


class CustomDateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        # kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)


class CustomDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"
    #input_type = "datetime"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%dT%H:%M"
        super().__init__(**kwargs)


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class ChooseDateForm(forms.Form):
    date = forms.DateField(widget=CustomDateInput(
        format=["%Y-%m-%d"], attrs={
            'min': get_next_working_day(datetime.datetime.now().date()).strftime("%Y-%m-%d"),
            'max': get_next_working_day((datetime.datetime.now() + timedelta(days=7)).date()).strftime("%Y-%m-%d"),
        }), label="Select Date", initial=get_next_working_day(datetime.date.today()), required=True, error_messages={
            'required': 'Please select date',
    })
    # doctor = CustomModelChoiceField(label="Select Doctor", queryset=Doctor.objects.all(
    # ), initial=list(Doctor.objects.all()))
    doctor = CustomModelChoiceField(label="Select Doctor", queryset=Doctor.objects.all(
    ), initial=list(Doctor.objects.all()), widget=forms.RadioSelect)
    # field_switch = forms.BooleanField(widget=forms.RadioSelect(
    #     choices=((True, 'Morning'), (False, 'Evening')),
    # ), label="Select Time Slot", initial=True, required=True, error_messages={
    #     'required': 'Please select time slot',
    # })


class GetOTPForm(forms.Form):
    phone_no = PhoneNumberField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': ('Phone'), 'pattern': '[789][0-9]{9}'}),       label=("Phone number"), required=True, error_messages={
        'required': 'Please enter phone number',
    })


class VerifyOTPForm(forms.Form):
    otp = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': ('Enetr OTP')}),       label=("Enter OTP"))


GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'))
BLOOD_GROUP_CHOICES = (('AB+', 'AB+'), ('AB-', 'AB-'), ('A+', 'A+'),
                       ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'))


class CustomBaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomBaseModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['required'] = 'required'


class PatientProfileForm(forms.ModelForm):
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)

    class Meta:
        model = PatientProfile
        fields = ['first_name', 'middle_name',
                  'last_name', 'age', 'address', 'email', 'gender', 'blood_group']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First Name'
                    
                },
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Last Name'
                },
            ),
            'middle_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Middle Name'
                },
            ),
            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Age'}
            ),
            'address': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control'
            }),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Email'
                }
            ),
            'gender': forms.RadioSelect(choices=GENDER_CHOICES),

        }

class PatientMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': ('Your message'),'rows':4}),       label=("Your message"))