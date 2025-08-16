from django.contrib import admin
from django.urls import path, include

from app.schools.views import school_list, school_detail, edit_reply, delete_reply, edit_comment, delete_comment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', school_list, name='home'),
    path('escuelas/', include('app.schools.urls', namespace='schools')),
    path('usuarios/', include('app.users.urls', namespace='users')),
]
