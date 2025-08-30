from django.urls import path
from app.schools.views import school_detail, careers_list
from app.base.views import register_school_view

app_name = 'school'
urlpatterns = [
    path('registro/', register_school_view, name='register'),
    path('<int:pk>/', school_detail, name='school_detail'),
    path('<int:pk>/careers/', careers_list, name='careers_list'),
]
