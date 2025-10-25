from django.urls import path

from app.schools.views import school_detail, careers_list, general_information, edit_school, create_school, \
    create_careers, update_career, photos_list, schooL_photos, delete_photos
from app.base.views import register_school_view

app_name = 'school'
urlpatterns = [
    path('registro/', register_school_view, name='register'),
    path('<int:pk>/', school_detail, name='school_detail'),
    path('<int:pk>/carreras/', careers_list, name='careers_list'),
    path('<int:pk>/informacion-general/', general_information, name='general_information'),
    path('editar-escuela/', edit_school, name='edit_school'),
    path('crear-escuela/', create_school, name='create_school'),
    path('crear-carrera/', create_careers, name='create_careers'),
    path("careers/update/<int:career_id>/", update_career, name="update_career"),
    path("<int:pk>/photos/", photos_list, name="photos_list"),
    path('photos/', schooL_photos, name='photos'),
    path('photos/delete/', delete_photos, name='delete_photos')
]
