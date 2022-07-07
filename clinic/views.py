from django.shortcuts import render

from doctor.models import Doctor

# Create your views here.

def home_view(request):
    template_page='clinic/index.html'
    doctors=Doctor.objects.all()
    print(doctors)
    template_context={
        'doctors':doctors
    }
    return render(request,template_page,context=template_context) 