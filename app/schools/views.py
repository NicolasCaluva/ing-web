from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm
from .models import School, Comment, Reply


# Create your views here.
def school_list(request):
    schools = School.objects.all()
    context = {
        'schools': schools
    }

    return render(request, 'school/school_list.html', context)

def school_detail(request, pk):
    school = get_object_or_404(School, pk=pk)
    comments = Comment.objects.filter(school=school).order_by('-created_at')
    context = {
        'school': school,
        'comments': comments
    }

    return render(request, 'school/school_detail.html', context)


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


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    school_pk = comment.school.pk
    comment.delete()
    return redirect('school_detail', pk=school_pk)


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
    else:
        form = ReplyForm(instance=reply)
    return render(request, 'school/edit_reply.html', {'form': form})


def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    school_pk = reply.school.pk
    reply.delete()
    return redirect('school_detail', pk=school_pk)
