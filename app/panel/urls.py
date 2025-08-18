from django.urls import path

from app.panel.views import list_users, delete_user

app_name = 'panel'

urlpatterns = [
    path('usuarios/', list_users, name='list_users'),
    path('usuarios/eliminar/<int:pk>/', delete_user, name='delete_user'),
]