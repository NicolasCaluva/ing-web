import googlemaps
from django.db.models import Q
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from dondeestudiar import settings
from .models import School, Career


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
        "is_school": False,
        "is_school_with_no_school": False,
    }
    if request.user.is_authenticated:
        if School.objects.filter(user__email=request.user.email).exists():
            is_school = True
            context["is_school"] = is_school
        elif request.user.email.endswith('@santafe.edu.ar'):
            context["is_school_with_no_school"] = True
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
def edit_school(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    school= School.objects.filter(user__email=request.user.email).first()
    if not school:
        return redirect(f"{reverse('home')}?next={request.path}")
    careers = Career.objects.filter(school=school)
    context = {
        "school": school,
        "careers": careers,
    }
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        profile_photo = request.FILES.get('profile_photo')
        logo = request.FILES.get('logo')
        general_description = request.POST.get('general_description', '').strip()
        income_description = request.POST.get('income_description', '').strip()
        shift = request.POST.getlist('shifts')

        if profile_photo:
            school.profile_photo = profile_photo
        if logo:
            school.logo = logo
        if name:
            if School.objects.filter(name=name).exclude(id=school.id).exists():
                context = {
                    "error": "Ya existe una escuela con ese nombre.",
                    "school": school,
                    "careers": careers,
                }
                return render(request, 'school/edit_school.html', context)
            school.name = name
        if address:
            school.address = address
        if phone_number:
            school.phone_number = phone_number
        if general_description:
            school.general_description = general_description
        if income_description:
            school.income_description = income_description
        if shift:
            school.shifts = shift
        for i, career in enumerate(careers, start=1):
            career.name = request.POST.get(f"career_name_{i}", career.name)
            career.scope = request.POST.get(f"career_scope_{i}", career.scope)
            career.duration = request.POST.get(f"career_duration_{i}", career.duration)
            career.save()

        school.save()
        context["school"] = school
        context["success"] = "Perfil de la escuela actualizado correctamente."
        return redirect(reverse('home'))
    return render(request, 'school/edit_school.html', context)

def create_school(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    if School.objects.filter(user__email=request.user.email).exists():
        return redirect(f"{reverse('home')}?next={request.path}")
    if not request.user.email.endswith('@santafe.edu.ar'):
        context = {
            "error": "El correo electrónico debe terminar con @santafe.edu.ar."
        }
        return render(request, 'school/create_school.html', context)
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        profile_photo = request.FILES.get('profile_photo')
        logo = request.FILES.get('logo')
        general_description = request.POST.get('general_description', '').strip()
        income_description = request.POST.get('income_description', '').strip()
        shift = request.POST.getlist('shifts')

        if not name or not address or not phone_number or not profile_photo or not logo or not general_description or not income_description or not shift:
            context = {
                "error": "Por favor, complete todos los campos obligatorios.",
            }
            return render(request, 'school/create_school.html', context)
        if School.objects.filter(name=name):
            context = {
                "error": "Ya existe una escuela con ese nombre.",
            }
            return render(request, 'school/create_school.html', context)
        school = School.objects.create(
            user=request.user,
            name=name,
            address=address,
            phone_number=phone_number,
            profile_photo=profile_photo,
            logo=logo,
            general_description=general_description,
            income_description=income_description,
            shifts=shift
        )
        if school.address:
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            geocode_result = gmaps.geocode(school.address)

            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                school.latitude = location['lat']
                school.longitude = location['lng']
        school.save()

        return redirect(reverse('school:create_careers'))

    return render(request, 'school/create_school.html')
def create_careers(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    school = School.objects.filter(user__email=request.user.email).first()
    if not school:
        return redirect(f"{reverse('home')}?next={request.path}")
    if request.method == "POST":
        career_name = request.POST.get('career_name', '').strip()
        career_scope = request.POST.get('career_scope', '').strip()
        career_duration = request.POST.get('career_duration', '').strip()
        origin=request.POST.get('origin','').strip()

        if not career_name or not career_scope or not career_duration:
            context = {
                "error": "Por favor, complete todos los campos obligatorios.",
                "careers": Career.objects.filter(school=school)
            }
            return render(request, 'school/create_careers.html', context)

        career = Career.objects.create(
            school=school,
            name=career_name,
            scope=career_scope,
            duration=career_duration
        )
        career.save()
        if origin=='edit_school':
            return redirect(reverse('school:edit_school'))
        return redirect(reverse('school:create_careers'))
    context = {
        "careers": Career.objects.filter(school=school)
    }
    return render(request, 'school/create_careers.html', context)
def update_career(request, career_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    school = School.objects.filter(user__email=request.user.email).first()
    if not school:
        return redirect(f"{reverse('home')}?next={request.path}")

    career = get_object_or_404(Career, id=career_id, school=school)

    if request.method == "POST":
        career_name = request.POST.get('career_name', '').strip()
        career_scope = request.POST.get('career_scope', '').strip()
        career_duration = request.POST.get('career_duration', '').strip()
        origin = request.POST.get('origin', '').strip()

        if not career_name or not career_scope or not career_duration:
            context = {
                "error": "Por favor, complete todos los campos obligatorios.",
                "careers": Career.objects.filter(school=school)
            }
            return render(request, 'school/create_careers.html', context)

        career.name = career_name
        career.scope = career_scope
        career.duration = career_duration
        career.save()
        if origin=='edit_school':
            return redirect(reverse('school:edit_school'))
        return redirect(reverse('school:create_careers'))