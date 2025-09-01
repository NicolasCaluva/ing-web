from django.urls import path

from app.base.views import register, verify_email, verification_mail_sent
from django.conf import settings
from django.conf.urls.static import static
app_name = 'base'

urlpatterns = [
    path('', register, name='register'),
    path("verify_email/", verify_email, name="verify_email"),
    path('verificacion-enviada/', verification_mail_sent, name='verification_mail_sent')
]