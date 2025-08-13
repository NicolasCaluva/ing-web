from django.contrib import admin

# Register your models here.
from .models import School, Comment

admin.site.register(School)
admin.site.register(Comment)