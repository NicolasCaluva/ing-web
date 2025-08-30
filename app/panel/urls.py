from django.urls import path

from app.panel.views import list_users, delete_user, upsert_user, list_schools, delete_school, upsert_school

app_name = 'panel'

urlpatterns = [
    path('', list_users, name='list_users'),
    path('usuarios/', list_users, name='list_users'),
    path('usuarios/eliminar/<int:pk>/', delete_user, name='delete_user'),
    path('usuarios/crear/', upsert_user, name='create_user'),
    path('usuarios/editar/<int:pk>/', upsert_user, name='edit_user'),

    path('escuelas/', list_schools, name='list_schools'),
    path('escuelas/eliminar/<int:pk>/', delete_school, name='delete_school'),
    path('escuelas/crear/', upsert_school, name='create_school'),
    path('escuelas/editar/<int:pk>/', upsert_school, name='edit_school')
]
