from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from app.base.views import logger
from app.schools.models import School
from app.users.models import UserBase


# Create your views here.

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def list_users(request):
    logger.info("Acceso a list_users por usuario: %s", request.user)
    if request.method == 'GET':
        users = UserBase.objects.all()
        logger.debug("Total usuarios: %d", users.count())
        context = {
            'users': users
        }
        return render(request, 'panel/list-users.html', context)

    else:
        logger.warning("Método no permitido en list_users: %s", request.method)
        return render(request, 'panel/list-users.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def delete_user(request, pk):
    logger.info("Acceso a delete_user id=%s por usuario: %s", pk, request.user)
    if request.method == 'POST':
        try:
            user = UserBase.objects.get(id=pk)
            user.user.is_active = False
            user.user.save()
            logger.info("Usuario desactivado: %s", user.user.email)
            return redirect(reverse('panel:list_users'))
        except UserBase.DoesNotExist:
            logger.error("Usuario no encontrado para id=%s", pk)
            return render(request, 'panel/list-users.html', {'error': 'Usuario no encontrado'})
        except Exception as e:
            logger.error("Error inesperado en delete_user: %s", str(e))
    else:
        logger.warning("Método no permitido en delete_user: %s", request.method)
        return render(request, 'panel/list-users.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def upsert_user(request, pk=None):
    logger.info("Acceso a upsert_user pk=%s por usuario: %s", pk, request.user)
    if request.method == 'GET':
        context = {}
        if pk:
            context['user'] = UserBase.objects.get(id=pk)
            logger.debug("Editando usuario: %s", context['user'].user.email)
        else:
            context['user'] = None
            logger.debug("Creando nuevo usuario")

        return render(request, 'panel/upsert-user.html', context)

    elif request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        logger.debug("Datos recibidos en upsert_user: %s, %s, %s", first_name, last_name, email)

        try:
            if pk:
                userbase = UserBase.objects.get(id=pk)
                userbase.user.first_name = first_name
                userbase.user.last_name = last_name
                userbase.user.email = email
                userbase.user.save()
                userbase.save()
                logger.info("Usuario actualizado: %s", email)
                messages.add_message(request, messages.SUCCESS, 'Usuario actualizado correctamente.')
            else:
                user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
                userbase = UserBase()
                userbase.user = user
                user.is_active = False
                userbase.generate_recovery_code()

                userbase.save()
                user.save()
                logger.info("Usuario creado: %s", email)


                # Acá iría la lógica de enviar código de recuperación por correo electrónico

                messages.add_message(request, messages.INFO,
                                     'Se envió un código de recuperación al correo electrónico proporcionado.')

            return redirect(reverse('panel:list_users'))
        except Exception as e:
            logger.error("Error en upsert_user: %s", str(e))
            return render(request, 'panel/list-users.html', {'error': 'Error inesperado'})


    else:
        logger.warning("Método no permitido en upsert_user: %s", request.method)
        return render(request, 'panel/list-users.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def list_schools(request):
    logger.info("Acceso a list_schools por usuario: %s", request.user)
    if request.method == 'GET':
        schools = School.objects.all()
        logger.debug("Total escuelas: %d", schools.count())
        context = {
            'schools': schools
        }
        return render(request, 'panel/list-schools.html', context)

    else:
        logger.warning("Método no permitido en list_schools: %s", request.method)
        return render(request, 'panel/list-schools.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def delete_school(request, pk):
    logger.info("Acceso a delete_school id=%s por usuario: %s", pk, request.user)
    if request.method == 'POST':
        if pk:
            try:
                school = School.objects.get(id=pk)
                school.user.is_active = False
                school.user.save()
                logger.info("Escuela desactivada: %s", school.name)
                messages.add_message(request, messages.SUCCESS, 'Escuela eliminada correctamente.')
                return redirect(reverse('panel:list_schools'))
            except School.DoesNotExist:
                logger.error("Escuela no encontrada para id=%s", pk)
                messages.add_message(request, messages.ERROR, 'Escuela no encontrada.')
                return redirect(reverse('panel:list_schools'))
            except Exception as e:
                logger.error("Error inesperado en delete_school: %s", str(e))
                messages.add_message(request, messages.ERROR, 'Error inesperado.')
                return redirect(reverse('panel:list_schools'))
        else:
            logger.warning("ID no proporcionado en delete_school")
            messages.add_message(request, messages.ERROR, 'El ID es requerido para eliminar una escuela.')
            return redirect(reverse('panel:list_schools'))
    else:
        logger.warning("Método no permitido en delete_school: %s", request.method)
        return render(request, 'panel/list-schools.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def upsert_school(request, pk=None):
    logger.info("Acceso a upsert_school pk=%s por usuario: %s", pk, request.user)
    if request.method == 'GET':
        context = {}
        if pk:
            context['school'] = School.objects.get(id=pk)
            logger.debug("Editando escuela: %s", context['school'].name)
        else:
            context['school'] = None
            logger.debug("Creando nueva escuela")

        return render(request, 'panel/upsert-school.html', context)

    elif request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        general_description = request.POST['general_description']
        income_description = request.POST['income_description']
        email = request.POST.get('email', None)
        profile_photo = request.FILES.get('profile_photo', None)
        logo = request.FILES.get('logo', None)
        logger.debug("Datos recibidos en upsert_school: %s, %s, %s", name, address, email)

        try:
            if pk:
                school = School.objects.get(id=pk)
                school.name = name
                school.address = address
                school.phone_number = phone_number
                school.general_description = general_description
                school.income_description = income_description
                school.logo = logo
                school.profile_photo = profile_photo
                school.save()
                logger.info("Escuela actualizada: %s", name)
                messages.add_message(request, messages.SUCCESS, 'Escuela actualizada correctamente.')
            else:
                user = User.objects.create_user(username=email, email=email)
                school = School(user=user, name=name, address=address, phone_number=phone_number,
                                general_description=general_description, income_description=income_description
                                , profile_photo=profile_photo, logo=logo)
                school.save()
                logger.info("Escuela creada: %s", name)
                messages.add_message(request, messages.INFO, 'Escuela creada correctamente.')
            return redirect(reverse('panel:list_schools'))

        except Exception as e:
            logger.error("Error en upsert_school: %s", str(e))
            return render(request, 'panel/list-schools.html', {'error': 'Error inesperado'})
    else:
        logger.warning("Método no permitido en upsert_school: %s", request.method)
        return render(request, 'panel/list-schools.html', {'error': 'Invalid request method'})
