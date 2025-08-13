from django.contrib import admin

# Register your models here.

from .models import UserBase
admin.site.register(UserBase)