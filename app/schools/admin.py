from django.contrib import admin

# Register your models here.
from .models import School, Tag, Career, Photo

admin.site.register(School)
admin.site.register(Tag)
admin.site.register(Photo)


@admin.register(Career)
class CareersAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
