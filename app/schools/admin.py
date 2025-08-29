from django.contrib import admin

# Register your models here.
from .models import School, Comment, Reply, Tag

admin.site.register(School)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Tag)