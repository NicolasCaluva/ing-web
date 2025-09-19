from django.contrib import admin
from .models import Comment, Reply
admin.site.register(Reply)
admin.site.register(Comment)

# Register your models here.
