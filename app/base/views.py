from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.text import slugify

from app.schools.models import School
from app.users.models import UserBase


# Create your views here.


def register(request):
    return render(request, 'base/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        return render(request, 'base/login.html')

    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            if User.objects.filter(username=email).exists():
                user = authenticate(username=email, password=password)
                if user:
                    login(request, user)
                    return redirect(reverse('home'))
                else:
                    return render(request, 'base/login.html',
                                  {'error': "El correo electrónico o la contraseña son incorrectos."})
            else:
                return render(request, 'base/login.html',
                              {'error': "El correo electrónico o la contraseña son incorrectos."})
        else:
            error_message = "Por favor, ingrese su correo electrónico y contraseña."
            return render(request, 'base/login.html', {'error': error_message})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, inicie sesión para continuar.')
        return redirect('users:login')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def register_user_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        return render(request, 'base/register_user.html')

    elif request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not (first_name and last_name and email and password and password2):
            error_message = "Por favor, complete todos los campos."
            return render(request, 'base/register_user.html', {'error': error_message})

        if password != password2:
            error_message = "Las contraseñas no coinciden."
            return render(request, 'base/register_user.html', {'error': error_message})

        if User.objects.filter(username=email).exists():
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_user.html', {'error': error_message})

        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        UserBase.objects.create(user=user)

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect(reverse('home'))
        else:
            return render(request, 'base/register_user.html',
                          {'error': "Hubo un problema al crear su cuenta. Por favor, inténtelo de nuevo."})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        return redirect('users:register')


def edit_user_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = UserBase.objects.get(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        profile_photo = request.FILES.get('profile_image')
        if profile_photo:
            user.profile_photo = profile_photo
        if first_name:
            user.user.first_name = first_name
        if last_name:
            user.user.last_name = last_name

        user.save()
        user.user.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect(reverse('home'))

    return render(request, 'base/edit_profile.html', {'user': user})

def register_school_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        return render(request, 'base/register_school.html')

    elif request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not (name and email and password and password2):
            error_message = "Por favor, complete todos los campos."
            return render(request, 'base/register_school.html', {'error': error_message})

        if password != password2:
            error_message = "Las contraseñas no coinciden."
            return render(request, 'base/register_school.html', {'error': error_message})

        if not email.endswith('@santafe.edu.ar'):
            error_message = "El correo electrónico debe terminar con @santafe.edu.ar."
            return render(request, 'base/register_school.html', {'error': error_message})

        if User.objects.filter(username=email).exists():
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_school.html', {'error': error_message})

        user = User.objects.create_user(username=email, email=email, password=password)
        slug = slugify(name)
        School.objects.create(user=user, name=name, slug=slug)

        # TODO: No se debe autenticar automáticamente a la escuela, primero se debe enviar un correo y que valide su cuenta desde el link que se le envió.
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect(reverse('home'))
        else:
            return render(request, 'base/register_school.html',
                          {'error': "Hubo un problema al crear su cuenta. Por favor, inténtelo de nuevo."})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        return redirect('users:register_school')