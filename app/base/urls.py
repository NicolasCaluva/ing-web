from django.urls import path

from app.base.views import register, verify_email

app_name = 'base'

urlpatterns = [
    path('', register, name='register'),
    path("verify_email/", verify_email, name="verify_email"),
]