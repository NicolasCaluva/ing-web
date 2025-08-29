from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from .forms import CommentForm, ReplyForm
from .models import School, Comment, Reply
from ..users.models import UserBase


# Create your views here.

def school_list(request):
    query = request.GET.get("search", "").strip()
    turno = request.GET.get("turno")

    schools = School.objects.all()

    # --- filtros ---
    if query:
        schools = schools.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(careers__name__icontains=query) |
            Q(tag__name__icontains=query)
        ).distinct()

    if turno:
        schools = schools.filter(shifts__contains=turno)

    # --- context unificado ---
    context = {
        "schools": schools,
        "user": request.user,
        "query": query,
        "turno": turno,
    }

    # --- respuesta con HTMX ---
    if request.headers.get("HX-Request") == "true":
        return render(request, "base/partials/school_cards.html", context)

    return render(request, "base/index.html", context)
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


def add_reply(request, pk, idComentario):
    school = get_object_or_404(School, pk=pk)
    comment = get_object_or_404(Comment, pk=idComentario)

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


def school_search(request):
    query = request.GET.get("q", "").strip()
    schools = School.objects.all()

    if query:
        schools = schools.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(careers__name__icontains=query)
        ).distinct()

    html = render_to_string("school/../../templates/base/partials/school_cards.html", {"schools": schools})
    return HttpResponse(html)
