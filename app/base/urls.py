from django.urls import path

from app.base.views import register, edit_user_view
from django.conf import settings
from django.conf.urls.static import static
app_name = 'base'

urlpatterns = [
    path('', register, name='register'),
    path('editar_perfil/', edit_user_view, name='edit_profile')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
