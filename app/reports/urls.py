from django.urls import path
from .views import report_comment

app_name = 'reports'

urlpatterns = [
    path('reportar/<int:pk>/<int:comment_id>/', report_comment, name='report_comment'),
]
