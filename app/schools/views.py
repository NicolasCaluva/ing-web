import googlemaps
import math

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from dondeestudiar import settings
from .models import School, Career
from haystack.query import SearchQuerySet
import logging
logger = logging.getLogger(__name__)

# Create your views here.
def rebuild_index(request):
    from django.core.management import call_command
    from django.http import JsonResponse
    try:
        call_command("rebuild_index", noinput=False)
        result = "Index rebuilt"
    except Exception as err:
        result = f"Error: {err}"

    return JsonResponse({"result": result})

# función auxiliar para calcular distancia en km
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # radio de la tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def school_list(request):
    query = request.GET.get("search", "").strip()
    turno = request.GET.get("turno")
    distance = request.GET.get("distance")
    user_lat = request.COOKIES.get("user_lat")
    user_lon = request.COOKIES.get("user_lon")

    if query:
        sqs = SearchQuerySet().models(School)
        schools_search = sqs.filter(content__icontains=query)
        school_ids = [result.pk for result in schools_search]
        schools = School.objects.filter(id__in=school_ids)
    else:
        schools = School.objects.all()

    if turno:
        schools = schools.filter(shifts__contains=turno)

    if distance and user_lat and user_lon:
        distance = float(distance)
        user_lat = float(user_lat)
        user_lon = float(user_lon)

        filtered_schools = []
        for s in schools:
            if s.latitude is not None and s.longitude is not None:
                s.distance = haversine(
                    user_lat,
                    user_lon,
                    float(s.latitude),
                    float(s.longitude)
                )
                if s.distance <= distance:
                    filtered_schools.append(s)
            else:
                s.distance = None
        schools = filtered_schools
    else:
        for s in schools:
            s.distance = None

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
            context["is_school"] = True
        elif request.user.email.endswith('@santafe.edu.ar'):
            context["is_school_with_no_school"] = True

    if request.headers.get("HX-Request") == "true":
        return render(request, "base/partials/school_cards.html", context)

    return render(request, "base/index.html", context)


def school_detail(request, pk):
    logger.info("Detalle de escuela pk=%s por usuario: %s", pk, request.user)
    school = get_object_or_404(School, pk=pk)

    if request.method == "GET":
        logger.debug("Método GET en school_detail")
        context = {
            'school': school,
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        }

        return render(request, 'school/school_detail.html', context)

    else:
        logger.warning("Método no permitido en school_detail: %s", request.method)
        return render(request, 'school/school_detail.html', {
            'school': school,
            'error': 'Método no permitido.'
        })


def school_search(request):
    logger.info("Acceso a school_search por usuario: %s", request.user)
    query = request.GET.get("q", "").strip()
    schools = School.objects.all()
    logger.debug("Total escuelas iniciales: %d", schools.count())

    if query:
        logger.info("Filtro de búsqueda: %s", query)
        schools = schools.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(careers__name__icontains=query)
        ).distinct()
        logger.debug("Escuelas tras filtro de búsqueda: %d", schools.count())

    html = render_to_string("school/../../templates/base/partials/school_cards.html", {"schools": schools})
    logger.debug("Renderizado parcial de school_cards")
    return HttpResponse(html)


def careers_list(request, pk):
    logger.info("Acceso a careers_list pk=%s por usuario: %s", pk, request.user)
    school = get_object_or_404(School, pk=pk)
    careers = school.careers.all()
    logger.debug("Total carreras: %d", careers.count())


    context = {
        'school': school,
        'careers': careers,
    }

    return render(request, 'school/partial/careers.html', context)


def general_information(request, pk):
    logger.info("Acceso a general_information pk=%s por usuario: %s", pk, request.user)

    school = get_object_or_404(School, pk=pk)

    context = {
        'school': school,
    }

    return render(request, 'school/partial/general_information.html', context)


def photos_list(request, pk):
    school = get_object_or_404(School, pk=pk)
    photos = school.photos.all()

    context = {
        'school': school,
        'photos': photos,
    }

    return render(request, 'school/partial/photos_detail.html', context)


@login_required
def edit_school(request):
    logger.info("Acceso a edit_school por usuario: %s", request.user)
    if not request.user.is_authenticated:
        logger.warning("Usuario no autenticado en edit_school")
        return redirect(f"{reverse('login')}?next={request.path}")
    school = School.objects.filter(user__email=request.user.email).first()

    if not school:
        logger.warning("No se encontró escuela para usuario: %s", request.user.email)
        return redirect(f"{reverse('home')}?next={request.path}")

    careers = Career.objects.filter(school=school)
    context = {
        "school": school,
        "careers": careers,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }

    if request.method == "POST":
        logger.debug("POST recibido en edit_school")
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
                logger.warning("Intento de nombre duplicado: %s", name)
                context = {
                    "error": "Ya existe una escuela con ese nombre.",
                    "school": school,
                    "careers": careers,
                    'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
                }
                return render(request, 'school/edit_school.html', context)
            school.name = name
        address_changed = False
        if address and address != school.address:
            school.address = address
            address_changed = True
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

        # Geocodificar si la dirección cambió
        if address_changed:
            try:
                gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                geocode_result = gmaps.geocode(school.address)
                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    school.latitude = location['lat']
                    school.longitude = location['lng']
                    logger.info("Coordenadas actualizadas para escuela: %s", school.name)
                else:
                    logger.warning("No se encontraron coordenadas para la dirección: %s", school.address)
            except Exception as e:
                logger.error("Error al geocodificar dirección: %s", str(e))

        school.save()
        logger.info("Perfil de escuela actualizado: %s", school.name)
        context["school"] = school
        context["success"] = "Perfil de la escuela actualizado correctamente."
        return redirect(reverse('home'))

    elif request.method == "GET":
        if request.headers.get("HX-Request") == "true":
            return render(request, 'school/partial/edit_data.html', context)
        return render(request, 'school/edit_school.html', context)

    return render(request, 'school/edit_school.html', context)


@login_required
def create_school(request):
    logger.info("Acceso a create_school por usuario: %s", request.user)
    if not request.user.is_authenticated:
        logger.warning("Usuario no autenticado en create_school")
        return redirect(f"{reverse('login')}?next={request.path}")

    if School.objects.filter(user__email=request.user.email).exists():
        logger.warning("Usuario ya tiene escuela: %s", request.user.email)
        return redirect(f"{reverse('home')}?next={request.path}")

    if not request.user.email.endswith('@santafe.edu.ar'):
        logger.warning("Email no válido para crear escuela: %s", request.user.email)
        context = {
            "error": "El correo electrónico debe terminar con @santafe.edu.ar."
        }
        return render(request, 'school/create_school.html', context)

    if request.method == "POST":
        logger.debug("POST recibido en create_school")
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        profile_photo = request.FILES.get('profile_photo')
        logo = request.FILES.get('logo')
        general_description = request.POST.get('general_description', '').strip()
        income_description = request.POST.get('income_description', '').strip()
        shift = request.POST.getlist('shifts')

        if not name or not address or not phone_number or not profile_photo or not logo or not general_description or not income_description or not shift:
            logger.warning("Campos obligatorios faltantes en create_school")
            context = {
                "error": "Por favor, complete todos los campos obligatorios.",
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY
            }
            return render(request, 'school/create_school.html', context)

        if School.objects.filter(name=name):
            logger.warning("Intento de nombre duplicado en create_school: %s", name)
            context = {
                "error": "Ya existe una escuela con ese nombre.",
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY
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
        logger.info("Escuela creada: %s", school.name)

        # Geocodificar la dirección para obtener coordenadas
        if school.address:
            try:
                gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                geocode_result = gmaps.geocode(school.address)
                
                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    school.latitude = location['lat']
                    school.longitude = location['lng']
                    logger.info("Coordenadas obtenidas para escuela: %s - lat: %s, lng: %s", 
                              school.name, school.latitude, school.longitude)
                else:
                    logger.warning("No se encontraron coordenadas para la dirección: %s", school.address)
            except Exception as e:
                logger.error("Error al geocodificar dirección en create_school: %s", str(e))
        
        school.save()

        return redirect(reverse('school:create_careers'))
    context = {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'school/create_school.html', context)


@login_required
def create_careers(request):
    logger.info("Acceso a create_careers por usuario: %s", request.user)
    if not request.user.is_authenticated:
        logger.warning("Usuario no autenticado en create_careers")
        return redirect(f"{reverse('login')}?next={request.path}")
    school = School.objects.filter(user__email=request.user.email).first()

    if not school:
        logger.warning("No se encontró escuela para usuario en create_careers: %s", request.user.email)
        return redirect(f"{reverse('home')}?next={request.path}")

    if request.method == "GET":
        logger.debug("GET recibido en create_careers")
        context = {
            "careers": Career.objects.filter(school=school),
            "school": school,
            "careers_context": True,
        }
        # Si es una petición HTMX, solo retorna el parcial
        if request.headers.get("HX-Request"):
            return render(request, 'school/create_careers.html', context)
        # Si no es HTMX, retorna la página completa
        return render(request, 'school/edit_school.html', context)

    if request.method == "POST":
        logger.debug("POST recibido en create_careers")
        career_name = request.POST.get('career_name', '').strip()
        career_scope = request.POST.get('career_scope', '').strip()
        origin = request.POST.get('origin', '').strip()
        career_dura = request.POST.get('career_duration', '').strip()

        if not career_dura.isdigit():
            context = {
                "error": "Error, La duracion de la carrera debe ser un numero entero mayor a 0",
                "careers": Career.objects.filter(school=school),
                "school": school,
                "careers_context": True,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            if origin == 'edit_school':
                return render(request, "school/edit_school.html", context)
            return render(request, 'school/edit_school.html', context)
        career_duration = int(career_dura)

        if career_duration <= 0:
            logger.warning("Duración de carrera inválida: %d", career_duration)
            context = {
                "error": "Error, La duracion de la carrera debe ser mayor a 0",
                "careers": Career.objects.filter(school=school),
                "school": school,
                "careers_context": True,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            if origin == 'edit_school':
                return render(request, 'school/edit_school.html', context)
            return render(request, 'school/edit_school.html', context)

        if not career_name or not career_scope or not career_duration:
            logger.warning("Campos obligatorios faltantes en create_careers")
            context = {
                "error": "Por favor, complete todos los campos obligatorios.",
                "careers": Career.objects.filter(school=school),
                "school": school,
                "careers_context": True,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            if origin == 'edit_school':
                return render(request, "school/edit_school.html", context)
            return render(request, 'school/edit_school.html', context)

        career = Career.objects.create(
            school=school,
            name=career_name,
            scope=career_scope,
            duration=career_duration
        )
        career.save()
        logger.info("Carrera creada: %s", career.name)

        # Después de crear exitosamente, redirigir a la página de edición con el tab de carreras activo
        return redirect(reverse('school:create_careers'))

    context = {
        "careers": Career.objects.filter(school=school),
        "school": school,
        "careers_context": True,
    }

    return render(request, 'school/create_careers.html', context)


@login_required
def update_career(request, career_id):
    logger.info("Acceso a update_career id=%s por usuario: %s", career_id, request.user)
    if not request.user.is_authenticated:
        logger.warning("Usuario no autenticado en update_career")
        return redirect(f"{reverse('login')}?next={request.path}")

    school = School.objects.filter(user__email=request.user.email).first()
    if not school:
        logger.warning("No se encontró escuela para usuario en update_career: %s", request.user.email)
        return redirect(f"{reverse('home')}?next={request.path}")

    career = get_object_or_404(Career, id=career_id, school=school)

    if request.method == "POST":
        logger.debug("POST recibido en update_career")
        career_name = request.POST.get('career_name', '').strip()
        career_scope = request.POST.get('career_scope', '').strip()
        origin = request.POST.get('origin', '').strip()
        career_dura = request.POST.get('career_duration', '').strip()

        if not career_dura.isdigit():
            context = {
                "error": "Error, La duracion de la carrera debe ser un numero entero mayor a 0",
                "careers": Career.objects.filter(school=school),
                "school": school,
                "careers_context": True,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            return render(request, "school/edit_school.html", context)
        career_duration = int(career_dura)

        if career_duration <= 0:
            logger.warning("Duración de carrera inválida en update_career: %d", career_duration)
            context = {
                "error": "Error, La duracion de la carrera debe ser mayor a 0",
                "careers": Career.objects.filter(school=school),
                "school": school,
                "careers_context": True,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            return render(request, 'school/edit_school.html', context)

        if not career_name or not career_scope or not career_duration:
            logger.warning("Campos obligatorios faltantes en update_career")
            context = {
                "error": "Por favor, complete todos los campos obligatorios.",
                "careers": Career.objects.filter(school=school),
                "school": school,
                "careers_context": True,
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
            }
            return render(request, "school/edit_school.html", context)

        career.name = career_name
        career.scope = career_scope
        career.duration = career_duration
        career.save()
        logger.info("Carrera actualizada: %s", career.name)

        # Después de actualizar exitosamente, redirigir a la página de edición
        return redirect(reverse('school:create_careers'))

    context = {
        "career": career,
        "school": school,
        "careers_context": True,
    }

    return render(request, 'school/edit_school.html', context)


@login_required
def schooL_photos(request):
    school = School.objects.filter(user__email=request.user.email).first()

    if not school:
        return redirect(f"{reverse('home')}?next={request.path}")

    if request.method == "GET":
        context = {
            "school": school,
            "photos": school.photos.all(),
            "photos_context": True,
        }
        # Verificar si es una petición HTMX (el header existe, no importa su valor)
        if request.headers.get("HX-Request"):
            return render(request, 'school/partial/photos.html', context)
        return render(request, 'school/edit_school.html', context)

    elif request.method == "POST":
        photos = request.FILES.getlist('photos')
        if not photos:
            context = {
                "error": "Por favor, suba al menos una foto.",
                "school": school,
                "photos": school.photos.all(),
                "photos_context": True,
            }
            return render(request, 'school/edit_school.html', context)

        # Guardar las fotos
        for photo in photos:
            school.photos.create(image=photo)

        logger.info("Fotos cargadas para escuela: %s", school.name)

        # Hacer redirect normal
        return redirect(reverse('school:photos'))

    context = {
        "school": school,
        "photos": school.photos.all(),
        "photos_context": True,
    }
    return render(request, 'school/edit_school.html', context)


@login_required
def delete_photos(request):
    if request.method == "POST":
        school = School.objects.filter(user__email=request.user.email).first()

        if not school:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró la escuela asociada a tu cuenta.'
            }, status=403)

        photo_ids = request.POST.getlist('photo_ids[]')

        if not photo_ids:
            return JsonResponse({
                'success': False,
                'message': 'No se seleccionaron fotos para eliminar.'
            }, status=400)

        deleted_count = 0
        deleted_ids = []
        errors = []

        for photo_id in photo_ids:
            try:
                photo = school.photos.get(id=int(photo_id))
                photo.image.delete()  # Elimina el archivo físico
                photo.delete()  # Elimina el registro de la base de datos
                deleted_count += 1
                deleted_ids.append(int(photo_id))
            except Exception as e:
                logger.error("Error eliminando foto id=%s: %s", photo_id, str(e))
                errors.append(f"Error al eliminar foto {photo_id}")

        logger.info("Eliminadas %d fotos de la escuela: %s", deleted_count, school.name)

        message = f"Se {'eliminó' if deleted_count == 1 else 'eliminaron'} {deleted_count} foto{'s' if deleted_count != 1 else ''} exitosamente."

        return JsonResponse({
            'success': True,
            'message': message,
            'deleted_count': deleted_count,
            'deleted_ids': deleted_ids,
            'errors': errors
        })

    return JsonResponse({
        'success': False,
        'message': 'Método no permitido.'
    }, status=405)
