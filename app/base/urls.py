from django.urls import path
from app.base.views import home

app_name = 'base'

urlpatterns = [
    path('', home, name='home'),
]