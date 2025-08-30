from django.urls import path

from app.base.views import register_user_view
from app.users.views import edit_user_view

app_name = 'users'

urlpatterns = [
    path('registro/', register_user_view, name='register'),
    path('editar_perfil/', edit_user_view, name='edit_profile'),
]
