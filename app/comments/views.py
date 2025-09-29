from django.shortcuts import render, get_object_or_404, redirect

from app.comments.forms import CommentForm, ReplyForm
from app.comments.models import Comment, Reply
from app.schools.models import School
from app.users.models import UserBase
import logging
logger = logging.getLogger('app.comments')

# Create your views here.


def comments_view(request, pk):
    school = get_object_or_404(School, pk=pk)
    comments = Comment.objects.filter(school=school).order_by('-created_at')

    if request.method == "GET":
        logger.info(f"Acceso a comentarios de escuela: {school.pk}")
        context = {
            'school': school,
            'comments': comments,
        }

        return render(request, 'school/partial/comments.html', context)

    elif request.method == "POST":
        if request.user.is_authenticated:
            logger.info(f"Intento de crear comentario por usuario: {request.user} en escuela: {school.pk}")
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.school = school
                comment.user = UserBase.objects.get(user=request.user)
                comment.score = form.cleaned_data['score']
                comment.save()
                logger.info(f"Comentario creado: {comment.pk} por usuario: {request.user}")
                return redirect('school:school_detail', pk=school.pk)
            else:
                logger.warning(f"Error en formulario de comentario por usuario: {request.user} - Errores: {form.errors}")
                return render(request, 'school/school_detail.html', {
                    'school': school,
                    'comments': comments,
                    'form_errors': form.errors
                })
        else:
            logger.warning(f"Intento de comentar sin autenticación en escuela: {school.pk}")
            return render(request, 'school/school_detail.html', {
                'school': school,
                'comments': comments,
                'error': 'Debes iniciar sesión para comentar.'
            })

    else:
        logger.warning(f"Método no permitido en comments_view: {request.method}")
        return render(request, 'school/school_detail.html', {
            'school': school,
            'comments': comments,
            'error': 'Método no permitido.'
        })


def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        logger.info(f"Intento de edición de comentario: {comment.pk} por usuario: {request.user}")
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            logger.info(f"Comentario editado: {comment.pk}")
            return redirect('school_detail', pk=comment.school.pk)
        else:
            logger.warning(f"Error al editar comentario: {comment.pk} - Errores: {form.errors}")
    else:
        logger.info(f"Acceso a formulario de edición de comentario: {comment.pk}")
        form = CommentForm(instance=comment)
    return render(request, 'school/school_detail.html', {'form': form})


def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if not request.user.is_authenticated:
        logger.warning(f"Intento de eliminar comentario sin autenticación: {comment.pk}")
        return render(request, 'school/school_detail.html', {
            'school': comment.school,
            'comments': Comment.objects.filter(school=comment.school),
            'error': 'Debes iniciar sesión para eliminar un comentario.'
        })

    if not (request.user.is_superuser or request.user.is_staff):
        logger.warning(f"Usuario sin permisos intenta eliminar comentario: {comment.pk}")
        return render(request, 'school/school_detail.html', {
            'school': comment.school,
            'comments': Comment.objects.filter(school=comment.school),
            'error': 'No tienes permisos para eliminar este comentario.'
        })
    logger.info(f"Comentario eliminado: {comment.pk} por usuario: {request.user}")
    comment.delete()
    return redirect('school:school_detail', pk=pk)


def edit_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.method == 'POST':
        logger.info(f"Intento de edición de respuesta: {reply.pk} por usuario: {request.user}")
        form = CommentForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            logger.info(f"Respuesta editada: {reply.pk}")
            return redirect('school_detail', pk=reply.school.pk)
        else:
            logger.warning(f"Error al editar respuesta: {reply.pk} - Errores: {form.errors}")
    else:
        logger.info(f"Acceso a formulario de edición de respuesta: {reply.pk}")
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            logger.info(f"Respuesta editada desde GET: {reply.pk}")
            form.save()
            return redirect('school_detail', pk=reply.school.pk)


def delete_reply(request, pk, _, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if not request.user.is_authenticated:
        logger.warning(f"Intento de eliminar respuesta sin autenticación: {reply.pk}")
        return render(request, 'school/school_detail.html', {
            'school': reply.school,
            'comments': Comment.objects.filter(school=reply.school),
            'error': 'Debes iniciar sesión para eliminar una respuesta.'
        })
    if not (request.user.is_superuser or request.user.is_staff):
        logger.warning(f"Usuario sin permisos intenta eliminar respuesta: {reply.pk}")
        return render(request, 'school/school_detail.html', {
            'school': reply.school,
            'comments': Comment.objects.filter(school=reply.school),
            'error': 'No tienes permisos para eliminar esta respuesta.'
        })
    logger.info(f"Respuesta eliminada: {reply.pk} por usuario: {request.user}")
    reply.delete()
    return redirect('school:school_detail', pk=pk)


def add_reply(request, pk, comment_id):
    school = get_object_or_404(School, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == "POST":
        if request.user.is_authenticated:
            logger.info(f"Intento de crear respuesta por usuario: {request.user} en comentario: {comment.pk}")
            form = ReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.parent = comment
                reply.school = school
                reply.description = form.cleaned_data['description']
                reply.user = UserBase.objects.get(user=request.user)
                logger.info(f"Respuesta creada: {reply.pk} por usuario: {request.user}")
                reply.save()
                return redirect('school:school_detail', pk=school.pk)
            else:
                logger.warning(f"Error en formulario de respuesta por usuario: {request.user} - Errores: {form.errors}")
        else:
            logger.warning(f"Intento de responder sin autenticación en comentario: {comment.pk}")
            return render(request, 'school/school_detail.html', {
                'school': school,
                'comment': comment,
                'error': 'Debes iniciar sesión para responder.'
            })
    else:
        logger.info(f"Acceso a formulario de respuesta para comentario: {comment.pk}")
        form = ReplyForm()

    return render(request, 'school/school_detail.html', {'form': form, 'comment': comment})
