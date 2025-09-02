from django.db.models import Q
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from .models import School


# Create your views here.

def school_list(request):
    query = request.GET.get("search", "").strip()
    turno = request.GET.get("turno")

    schools = School.objects.all()

    # --- filtros ---
    if query:
        schools = schools.filter(
            Q(name__icontains=query) |
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

    if request.method == "GET":
        context = {
            'school': school,
        }

        return render(request, 'school/school_detail.html', context)

    else:
        return render(request, 'school/school_detail.html', {
            'school': school,
            'error': 'Método no permitido.'
        })


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


def careers_list(request, pk):
    school = get_object_or_404(School, pk=pk)
    careers = school.careers.all()

    context = {
        'school': school,
        'careers': careers,
    }

    return render(request, 'school/partial/careers.html', context)


def general_information(request, pk):
    school = get_object_or_404(School, pk=pk)

    context = {
        'school': school,
    }

    return render(request, 'school/partial/general_information.html', context)
