from django.contrib import admin
from django.urls import path, include

from app.schools.views import school_list, school_detail, edit_reply, delete_reply, edit_comment, delete_comment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', school_list, name='home'),
    path('schools/<int:pk>/', school_detail, name='school_detail'),
    path('comment/<int:pk>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete_comment'),
    path('reply/<int:pk>/edit/', edit_reply, name='edit_reply'),
    path('reply/<int:pk>/delete/', delete_reply, name='delete_reply'),
]