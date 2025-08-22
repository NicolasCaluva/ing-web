from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from app.schools.models import School
from app.users.models import UserBase


# Create your views here.

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def list_users(request):
    if request.method == 'GET':
        users = UserBase.objects.all()
        context = {
            'users': users
        }
        return render(request, 'panel/list-users.html', context)

    else:
        return render(request, 'panel/list-users.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def delete_user(request, pk):
    if request.method == 'POST':
        try:
            user = UserBase.objects.get(id=pk)
            user.user.is_active = False
            user.user.save()
            return redirect(reverse('panel:list_users'))
        except UserBase.DoesNotExist:
            return render(request, 'panel/list-users.html', {'error': 'Usuario no encontrado'})
    else:
        return render(request, 'panel/list-users.html', {'error': 'Invalid request method'})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def upsert_user(request, pk=None):
    if request.method == 'GET':
        context = {}
        if pk:
            context['user'] = UserBase.objects.get(id=pk)
        else:
            context['user'] = None

        return render(request, 'panel/upsert-user.html', context)

    elif request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']

        if pk:
            userbase = UserBase.objects.get(id=pk)
            userbase.user.first_name = first_name
            userbase.user.last_name = last_name
            userbase.user.email = email
            userbase.user.save()
            userbase.save()
            messages.add_message(request, messages.SUCCESS, 'Usuario actualizado correctamente.')
        else:
            user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
            userbase = UserBase()
            userbase.user = user
            user.is_active = False
            userbase.generate_recovery_code()

            userbase.save()
            user.save()
            # Acá iría la lógica de enviar código de recuperación por correo electrónico

            messages.add_message(request, messages.INFO,
                                 'Se envió un código de recuperación al correo electrónico proporcionado.')

        return redirect(reverse('panel:list_users'))

    else:
        return render(request, 'panel/list-users.html', {'error': 'Invalid request method'})



@login_required
@user_passes_test(lambda u: u.is_staff, login_url='base:login')
def list_schools(request):
    if request.method == 'GET':
        schools = School.objects.all()
        context = {
            'schools': schools
        }
        return render(request, 'panel/list-schools.html', context)

    else:
        return render(request, 'panel/list-schools.html', {'error': 'Invalid request method'})