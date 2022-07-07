from django.contrib import admin
from .models import User

# Register your models here.

admin.site.site_header = 'Diya Eye Care Admin'

admin.site.register(User)
