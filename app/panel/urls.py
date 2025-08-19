from django.urls import path

from app.panel.views import list_users, delete_user, upsert_user

app_name = 'panel'

urlpatterns = [
    path('', list_users, name='list_users'),
    path('usuarios/', list_users, name='list_users'),
    path('usuarios/eliminar/<int:pk>/', delete_user, name='delete_user'),
    path('usuarios/crear/', upsert_user, name='create_user'),
    path('usuarios/editar/<int:pk>/', upsert_user, name='edit_user'),
]
