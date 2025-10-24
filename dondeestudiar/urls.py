from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

from app.schools.views import school_list, rebuild_index
from app.base.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', school_list, name='home'),
    path('robots.txt', TemplateView.as_view(template_name="base/robots.txt", content_type="text/plain")),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('escuelas/', include('app.schools.urls', namespace='schools')),
    path('usuarios/', include('app.users.urls', namespace='users')),
    path('base/', include('app.base.urls', namespace='base')),
    path('panel/', include('app.panel.urls', namespace='panel')),
    path('reportes/', include(('app.reports.urls', 'reports'), namespace='reports')),
    path('comentarios/', include(('app.comments.urls', 'comments'), namespace='comments')),
    path('rebuild_index/', rebuild_index, name='rebuild_index')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
