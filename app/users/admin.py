from django.contrib import admin

# Register your models here.

from .models import UserBase


@admin.register(UserBase)
class UserBaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'user__first_name', 'user__last_name', 'user__is_staff', 'user__is_active',
                    'user__date_joined')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
