from django.contrib import admin
from .models import Comment
from .models import Reply

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'school')
    search_fields = ('author', 'text')
    list_filter = ('author', 'school')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'school')
    search_fields = ('author', 'text')
    list_filter = ('author', 'school')

admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)