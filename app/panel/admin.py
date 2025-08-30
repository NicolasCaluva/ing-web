from django.contrib import admin

# Register your models here.

from app.reports.models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'reason', 'created_at', 'is_reviewed']
    list_filter = ['is_reviewed']
    search_fields = ('user__username', 'comment__description', 'reason')
    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        updated_count = queryset.update(reviewed=True)
        self.message_user(request, f'{updated_count} reports marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected reports as reviewed"