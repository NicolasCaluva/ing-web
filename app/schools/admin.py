from django.contrib import admin

# Register your models here.
from .models import School, Tag

admin.site.register(School)
admin.site.register(Tag)