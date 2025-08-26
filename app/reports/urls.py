from django.urls import path
from . import views
from .views import report_comment

urlpatterns = [
    path('reportar/<int:pk>/<int:idComentario>/', report_comment, name='report_comment'),
]