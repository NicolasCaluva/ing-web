from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.text import slugify

from app.schools.models import School
from app.users.models import UserBase
from dondeestudiar import settings


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
                    next_url = request.POST.get('next')
                    if next_url:
                        return redirect(next_url)
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

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_user.html', {'error': error_message})

        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)

        userbase = UserBase.objects.create(user=user)
        userbase.save()
        code = userbase.generate_auth_code()

        verification_link = request.build_absolute_uri(
            reverse("base:verify_email") + f"?code={code}"
        )

        send_mail(
            subject="Verifica tu cuenta",
            message=f"Hola {first_name},\n\nPor favor verifica tu cuenta haciendo clic en el siguiente enlace:\n{verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect(reverse('base:verification_mail_sent'))
        else:
            return render(request, 'base/register_user.html',
                          {'error': "Hubo un problema al crear su cuenta. Por favor, inténtelo de nuevo."})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        return redirect('users:register')


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

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_school.html', {'error': error_message})

        user = User.objects.create_user(username=email, email=email, password=password)
        slug = slugify(name)
        school = School.objects.create(user=user, name=name, slug=slug)
        school.email_verified = False
        school.save()

        code = school.user.userbase.generate_auth_code()

        user = authenticate(username=email, password=password)

        verification_link = request.build_absolute_uri(
            reverse("base:verify_email") + f"?code={code}"
        )

        send_mail(
            subject="Verifica tu cuenta de escuela",
            message=f"Hola {name},\n\nPor favor verifica tu cuenta haciendo clic en el siguiente enlace:\n{verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        if user:
            login(request, user)
            return redirect(reverse('base:verification_mail_sent'))
        else:
            return render(request, 'base/register_school.html',
                          {'error': "Hubo un problema al crear su cuenta. Por favor, inténtelo de nuevo."})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        return redirect('users:register_school')


def verify_email(request):
    code = request.GET.get("code")
    if not code:
        return render(request, "base/verify_email.html", {"error": "Código inválido."})

    try:
        userbase = UserBase.objects.get(recovery_code=code)
    except UserBase.DoesNotExist:
        return render(request, "base/verify_email.html", {"error": "Código inválido o expirado."})

    userbase.email_verified = True
    userbase.recovery_code = None
    userbase.user.is_active = True
    userbase.user.save()
    userbase.save()

    messages.success(request, "Tu cuenta ha sido verificada. Ahora puedes iniciar sesión.")
    return redirect("login")

def verification_mail_sent(request):
    return render(request, 'base/verify_email_sent.html')