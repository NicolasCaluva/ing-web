from django.urls import path

from app.schools.views import school_detail

app_name = 'schools'

urlpatterns = [
    path('schools/<int:pk>/', school_detail, name='school_detail'),
]