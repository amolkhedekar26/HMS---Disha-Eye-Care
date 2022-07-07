from django.urls import path

from .views import home_view

app_name = 'clinic'

urlpatterns = [
    path('', home_view, name='home'),

]
