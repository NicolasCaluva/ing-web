from django.contrib import admin

# Register your models here.

from .models import UserBase

@admin.register(UserBase)
class UserBaseAdmin(admin.ModelAdmin):

    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)