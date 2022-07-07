from django.urls import path
from .views import home, login

app_name = 'users'

urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
]
