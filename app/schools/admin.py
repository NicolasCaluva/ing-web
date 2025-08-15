from django.contrib import admin

# Register your models here.
from .models import School, Comment, Reply

admin.site.register(School)
admin.site.register(Comment)
admin.site.register(Reply)