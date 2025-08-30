from django.urls import path
from app.schools.views import school_list, school_detail, delete_comment, edit_comment, edit_reply, delete_reply, \
    add_reply, school_search
from app.base.views import register_school_view
from django.conf import settings
from django.conf.urls.static import static

app_name = 'school'
urlpatterns = [
    path('registro/', register_school_view, name='register'),
    path('<int:pk>/', school_detail, name='school_detail'),
    path('<int:pk>/', edit_comment, name='edit_comment'),
    path('<int:pk>/comentario/<int:idComentario>/', delete_comment, name='delete_comment'),
    path('<int:pk>/', edit_reply, name='edit_reply'),
    path('<int:pk>/comentario/<int:idComentario>/respuesta/<int:idRespuesta>/', delete_reply, name='delete_reply'),
    path('<int:pk>/comentario/<int:idComentario>/respuesta/', add_reply, name='add_reply'),
]
