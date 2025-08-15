from django.contrib import admin

# Register your models here.

from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'reason', 'created_at', 'reviewed')
    list_filter = ('reviewed', 'created_at')
    search_fields = ('user__username', 'comment__description', 'reason')
    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        updated_count = queryset.update(reviewed=True)
        self.message_user(request, f'{updated_count} reports marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected reports as reviewed"