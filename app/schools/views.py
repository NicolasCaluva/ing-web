from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm, ReplyForm
from .models import School, Comment, Reply
from ..users.models import UserBase


# Create your views here.
def school_list(request):
    schools = School.objects.all()
    context = {
        'schools': schools,
        'user': request.user
    }
    return render(request, 'base/index.html', context)

def school_detail(request, pk):
    school = get_object_or_404(School, pk=pk)
    comments = Comment.objects.filter(school=school).order_by('-created_at')

    if request.method == "GET":
        context = {
            'school': school,
            'comments': comments
        }

        return render(request, 'school/school_detail.html', context)
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
                'error': 'Debes iniciar sesión para comentar.'
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
    return render(request, 'edit_comment.html', {'form': form})


def delete_comment(request, pk, idComentario):
    comment = get_object_or_404(Comment, pk=idComentario)
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


def delete_reply(request, pk, idComentario, idRespuesta):
    reply = get_object_or_404(Reply, pk=idRespuesta)
    reply.delete()
    return redirect('school:school_detail', pk=pk)

