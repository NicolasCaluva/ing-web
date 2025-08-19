from django.urls import path

from app.base.views import register_user_view

app_name = 'users'

urlpatterns = [
    path('registro/', register_user_view, name='register'),
]
