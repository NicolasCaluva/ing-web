from django.urls import path

from app.schools.views import school_list, school_detail, delete_comment, edit_comment, edit_reply, delete_reply

app_name = 'school'

urlpatterns = [
    path('', school_list, name='school_list'),
    path('<int:pk>/', school_detail, name='school_detail'),
    path('<int:pk>/', edit_comment, name='edit_comment'),
    path('<int:pk>/comentario/<int:idComentario>/', delete_comment, name='delete_comment'),
    path('<int:pk>/', edit_reply, name='edit_reply'),
    path('<int:pk>/comentario/<int:idComentario>/respuesta/<int:idRespuesta>/', delete_reply, name='delete_reply'),
]
