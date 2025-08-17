from django.urls import path

from app.base.views import index

app_name = 'base'

urlpatterns = [
    path('', index, name='index')
]
