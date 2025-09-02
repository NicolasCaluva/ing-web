from django.contrib import admin

# Register your models here.
from .models import School, Tag, Career

admin.site.register(School)
admin.site.register(Tag)


@admin.register(Career)
class CareersAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
