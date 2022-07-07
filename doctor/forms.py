from django import forms

from users.models import User
from .models import Doctor, TimeSlot


class DoctorUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'middle_name',
                  'last_name', 'phone_no', 'address', 'qualification', 'experience', 'specialization', 'fees', 'timings', 'profile_image', 'certificate_image']


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['day', 'start_time', 'end_time', 'half_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    # def clean(self):
    #     day = self.cleaned_data['day']
    #     start_time = self.cleaned_data['start_time']
    #     end_time = self.cleaned_data['end_time']
    #     half_time = self.cleaned_data['half_time']
    #     # time_slot = TimeSlot.objects.filter(
    #     #     day=day, start_time=start_time, end_time=end_time, half_time=half_time)
    #     # if time_slot.exists():
    #     #     raise forms.ValidationError("Time Slot already exists")
    #     # time_slot, created = TimeSlot.objects.get_or_create(
    #     #     day=day, start_time=start_time, end_time=end_time, half_time=half_time)
    #     # print(created)
    #     return self.cleaned_data

    # def save(self,commit=True):
    #     time_slot = super(TimeSlotForm, self).save(commit=False)
    #     time_slot.day = self.cleaned_data['day'].title()
    #     time_slot.half_time = self.cleaned_data['half_time'].title()
    #     if commit:
    #         time_slot.save()
    #     return time_slot


DAY_CHOICES = (('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
               ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'))


def get_today_day():
    import datetime
    today = datetime.datetime.now()
    return f'{today.strftime("%A")}'


class GetTimeSlotForm(forms.Form):
    days = forms.ChoiceField(choices=DAY_CHOICES, widget=forms.RadioSelect(
        attrs={'class': 'form-control'},
    ), initial=get_today_day
    )

class TimePickerInput(forms.TimeInput):
        input_type = 'time'

class EditTimeSlotForm(forms.ModelForm):
    # start_time = forms.TimeField(
    #     input_formats=['%I:%M %p'],
    #     widget=TimePickerInput(
    #     attrs={'class': 'form-control'},
    #     format='%I:%M %p'
    # ))
    # end_time = forms.TimeField(
    #     input_formats=['%I:%M %p'],
    #     widget=TimePickerInput(
    #     attrs={'class': 'form-control'},
    #     format='%I:%M %p'
    # ))
    class Meta:
        model = TimeSlot
        fields = ['day', 'start_time', 'end_time']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'start_time': TimePickerInput(
                attrs={'class': 'form-control'},
            ),
            'end_time': TimePickerInput(
                attrs={'class': 'form-control'},
            ),
        }

class AddTimeSlotForm(forms.Form):
    days=forms.MultipleChoiceField(choices=DAY_CHOICES, widget=forms.CheckboxSelectMultiple(
       
    ))
    start_time = forms.TimeField(
        widget=TimePickerInput(
        attrs={'class': 'form-control'},
    ))
    end_time = forms.TimeField(
        widget=TimePickerInput(
        attrs={'class': 'form-control'},
    ))


class EditDoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'middle_name',
                  'last_name', 'phone_no', 'address', 'qualification', 'experience', 'specialization', 'fees', 'timings', 'profile_image', 'certificate_image']
        
        