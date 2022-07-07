from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from .forms import UserLoginForm

# Create your views here.


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()


def is_receptionist(user):
    return user.groups.filter(name='RECEPTIONIST').exists()


class HomePageView(TemplateView):
    template_name = 'users/index.html'


def home(request):
    template_page = 'users/index.html'
    if request.user.is_authenticated:
        if is_doctor(request.user):
            return redirect(reverse('doctor:home'))
        elif is_receptionist(request.user):
            return redirect(reverse('receptionist:home'))
        # else:
        #     return redirect(reverse('patient:home'))
        
    template_context = {
        
    }
    return render(request, template_page, context=template_context)


def login(request):
    login_form = UserLoginForm()

    template_context = {
        'login_form': login_form
    }

    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        print(login_form)
        if login_form.is_valid():
            return render(request, 'users/index.html')

    return render(request, 'users/login.html', context=template_context)
