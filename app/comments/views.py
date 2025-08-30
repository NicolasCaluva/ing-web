from django.shortcuts import render, get_object_or_404, redirect

from app.comments.forms import CommentForm, ReplyForm
from app.comments.models import Comment, Reply
from app.schools.models import School
from app.users.models import UserBase


# Create your views here.


def comments_view(request, pk):
    school = get_object_or_404(School, pk=pk)
    comments = Comment.objects.filter(school=school).order_by('-created_at')

    if request.method == "GET":
        context = {
            'school': school,
            'comments': comments,
        }

        return render(request, 'school/partial/comments.html', context)

    elif request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.school = school
                comment.user = UserBase.objects.get(user=request.user)
                comment.score = form.cleaned_data['score']
                comment.save()
                return redirect('school:school_detail', pk=school.pk)
            else:
                return render(request, 'school/school_detail.html', {
                    'school': school,
                    'comments': comments,
                    'form_errors': form.errors
                })
        else:
            return render(request, 'school/school_detail.html', {
                'school': school,
                'comments': comments,
                'error': 'Debes iniciar sesión para comentar.'
            })

    else:
        return render(request, 'school/school_detail.html', {
            'school': school,
            'comments': comments,
            'error': 'Método no permitido.'
        })


def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('school_detail', pk=comment.school.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'school/school_detail.html', {'form': form})


def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if not request.user.is_authenticated:
        return render(request, 'school/school_detail.html', {
            'school': comment.school,
            'comments': Comment.objects.filter(school=comment.school),
            'error': 'Debes iniciar sesión para eliminar un comentario.'
        })

    if not (request.user.is_superuser or request.user.is_staff):
        return render(request, 'school/school_detail.html', {
            'school': comment.school,
            'comments': Comment.objects.filter(school=comment.school),
            'error': 'No tienes permisos para eliminar este comentario.'
        })

    comment.delete()
    return redirect('school:school_detail', pk=pk)


def edit_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect('school_detail', pk=reply.school.pk)
    else:
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect('school_detail', pk=reply.school.pk)


def delete_reply(request, pk, _, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if not request.user.is_authenticated:
        return render(request, 'school/school_detail.html', {
            'school': reply.school,
            'comments': Comment.objects.filter(school=reply.school),
            'error': 'Debes iniciar sesión para eliminar una respuesta.'
        })
    if not (request.user.is_superuser or request.user.is_staff):
        return render(request, 'school/school_detail.html', {
            'school': reply.school,
            'comments': Comment.objects.filter(school=reply.school),
            'error': 'No tienes permisos para eliminar esta respuesta.'
        })
    reply.delete()
    return redirect('school:school_detail', pk=pk)


def add_reply(request, pk, comment_id):
    school = get_object_or_404(School, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.method == "POST":
        if request.user.is_authenticated:
            form = ReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.parent = comment
                reply.school = school
                reply.description = form.cleaned_data['description']
                reply.user = UserBase.objects.get(user=request.user)
                reply.save()
                return redirect('school:school_detail', pk=school.pk)
        else:
            return render(request, 'school/school_detail.html', {
                'school': school,
                'comment': comment,
                'error': 'Debes iniciar sesión para responder.'
            })
    else:
        form = ReplyForm()

    return render(request, 'school/school_detail.html', {'form': form, 'comment': comment})
