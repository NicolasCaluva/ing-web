from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.text import slugify

from app.schools.models import School
from app.users.models import UserBase
import logging
logger = logging.getLogger(__name__)

# Create your views here.


def register(request):
    logger.info("Acceso a formulario de registro")
    return render(request, 'base/register.html')


def login_view(request):
    if request.user.is_authenticated:
        logger.info(f"Usuario ya autenticado: {request.user}")
        return redirect('home')

    if request.method == 'GET':
        logger.info("Acceso a formulario de login")
        return render(request, 'base/login.html')

    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        logger.info(f"Intento de login para: {email}")
        if email and password:
            if User.objects.filter(username=email).exists():
                user = authenticate(username=email, password=password)
                if user:
                    logger.info(f"Login exitoso para: {email}")
                    login(request, user)
                    next_url = request.POST.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect(reverse('home'))
                else:
                    logger.warning(f"Login fallido: credenciales incorrectas para {email}")
                    return render(request, 'base/login.html',
                                  {'error': "El correo electrónico o la contraseña son incorrectos."})
            else:
                logger.warning(f"Login fallido: usuario no existe {email}")
                return render(request, 'base/login.html',
                              {'error': "El correo electrónico o la contraseña son incorrectos."})
        else:
            logger.warning("Login fallido: campos incompletos")
            if not email and not password:
                error_message = "Por favor, ingrese su correo electrónico y contraseña."
            elif not email:
                error_message = "Por favor, ingrese su correo electrónico."
            else:
                error_message = "Por favor, ingrese su contraseña."

            return render(request, 'base/login.html', {'error': error_message})

    else:
        logger.info("Acceso a login por método no soportado")
        messages.add_message(request, messages.INFO, 'Por favor, inicie sesión para continuar.')
        return redirect('users:login')


def logout_view(request):
    logger.info(f"Logout de usuario: {request.user}")
    request.session.flush()
    return redirect('login')


def register_user_view(request):
    if request.user.is_authenticated:
        logger.info(f"Usuario autenticado intenta acceder a registro: {request.user}")
        return redirect('home')

    if request.method == 'GET':
        logger.info("Acceso a formulario de registro de usuario")
        return render(request, 'base/register_user.html')

    elif request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        logger.info(f"Intento de registro de usuario: {first_name} {last_name} ({email})")

        if not (first_name and last_name and email and password and password2):
            logger.warning(f"Registro fallido: campos incompletos. Email: {email}")
            error_message = "Por favor, complete todos los campos."
            return render(request, 'base/register_user.html', {'error': error_message})

        if password != password2:
            logger.warning(f"Registro fallido: contraseñas no coinciden. Email: {email}")
            error_message = "Las contraseñas no coinciden."
            return render(request, 'base/register_user.html', {'error': error_message})

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            logger.warning(f"Registro fallido: email ya registrado. Email: {email}")
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_user.html', {'error': error_message})

        # Crear usuario y userbase — sin envío de email ni verificación adicional
        try:
            user = User.objects.create_user(username=email, email=email, password=password,
                                            first_name=first_name, last_name=last_name, is_active=True)
            logger.info(f"Usuario creado y activado: {email}")
            userbase = UserBase.objects.create(user=user, email_verified=True)
            userbase.save()
            logger.info(f"UserBase creado y marcado como verificado para: {email}")
        except Exception as e:
            logger.exception(f"Error crítico creando usuario {email}: {e}")
            return render(request, 'base/register_user.html', {'error': "Error al crear la cuenta. Por favor, intente nuevamente."})

        # Mostrar el mismo formulario pero con mensaje de éxito
        return render(request, 'base/register_user.html', {'success': True})

    else:
        logger.info("Acceso a registro de usuario por método no soportado")
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        return redirect('users:register')


def register_school_view(request):
    if request.user.is_authenticated:
        logger.info(f"Usuario autenticado intenta acceder a registro de escuela: {request.user}")
        return redirect('home')

    if request.method == 'GET':
        logger.info("Acceso a formulario de registro de escuela")
        return render(request, 'base/register_school.html')

    elif request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        logger.info(f"Intento de registro de escuela: {name} ({email})")
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not (name and email and password and password2):
            logger.warning(f"Registro de escuela fallido: campos incompletos. Email: {email}")
            error_message = "Por favor, complete todos los campos."
            return render(request, 'base/register_school.html', {'error': error_message})

        if password != password2:
            logger.warning(f"Registro de escuela fallido: contraseñas no coinciden. Email: {email}")
            error_message = "Las contraseñas no coinciden."
            return render(request, 'base/register_school.html', {'error': error_message})

        if not email.endswith('@santafe.edu.ar'):
            logger.warning(f"Registro de escuela fallido: email no válido. Email: {email}")
            error_message = "El correo electrónico debe terminar con @santafe.edu.ar."
            return render(request, 'base/register_school.html', {'error': error_message})

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            logger.warning(f"Registro de escuela fallido: email ya registrado. Email: {email}")
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_school.html', {'error': error_message})

        try:
            # Crear usuario activo directamente
            user = User.objects.create_user(username=email, email=email, password=password, is_active=True)
            logger.info(f"Usuario de escuela creado y activado: {email}")

            # Crear UserBase para la escuela y marcar verificado
            userbase = UserBase.objects.create(user=user, email_verified=True)
            userbase.save()
            logger.info(f"UserBase creado y marcado como verificado para escuela: {email}")

            slug = slugify(name)
            school = School.objects.create(user=user, name=name, slug=slug)
            school.email_verified = True
            school.save()
            logger.info(f"Escuela creada y marcada como verificada: {name}")

        except Exception as e:
            logger.exception(f"Error crítico durante registro de escuela {email}: {e}")
            return render(request, 'base/register_school.html', {'error': "Error al crear la cuenta. Por favor, intente nuevamente."})

        # Mostrar el mismo formulario pero con mensaje de éxito
        return render(request, 'base/register_school.html', {'success': True})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        logger.info("Acceso a registro de escuela por método no soportado")
        return redirect('users:register_school')
