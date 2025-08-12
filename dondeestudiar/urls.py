from django.contrib import admin
from django.urls import path, include

from app.schools.views import school_list, school_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', school_list, name='school_list'),
    path('<int:pk>/', school_detail, name='school_detail'),
]