from django.urls import path

from app.comments.views import comments_view, edit_comment, delete_comment, edit_reply, delete_reply, add_reply

app_name = 'comments'
urlpatterns = [
    path('<int:pk>/', comments_view, name='comments_list'),
    path('<int:pk>/', edit_comment, name='edit_comment'),
    path('<int:pk>/comentario/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('<int:pk>/', edit_reply, name='edit_reply'),
    path('<int:pk>/comentario/<int:comment_id>/respuesta/<int:reply_id>/', delete_reply, name='delete_reply'),
    path('<int:pk>/comentario/<int:comment_id>/respuesta/', add_reply, name='add_reply'),
]
