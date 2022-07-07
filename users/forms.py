from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
