from django.urls import path
from .views import report_comment

app_name = 'reports'

urlpatterns = [
    path('report/<int:pk>/<int:comment_id>/', report_comment, name='report_comment'),
]
