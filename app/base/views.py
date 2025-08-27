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

        if User.objects.filter(username=email).exists():
            error_message = "El correo electrónico ya está registrado."
            return render(request, 'base/register_user.html', {'error': error_message})

        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        user.save()

        userbase  = UserBase.objects.create(user=user)
        userbase.email_verified = False
        userbase.save()
        code = userbase.generate_recovery_code()

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
            return redirect(reverse('home'))
        else:
            return render(request, 'base/register_user.html',
                          {'error': "Hubo un problema al crear su cuenta. Por favor, inténtelo de nuevo."})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        return redirect('users:register')


def edit_user_view(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    user = UserBase.objects.get(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        new_email = request.POST.get('new_email', '').strip()
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        repeat_password = request.POST.get('repeat_password', '').strip()
        profile_photo = request.FILES.get('profile_image')
        if profile_photo:
            user.profile_photo = profile_photo


        if any([first_name, last_name, new_email, new_password]) and not current_password:
            return render(request, 'base/edit_profile.html', {
                'error': "Debe ingresar su contraseña actual para realizar cambios.",
                'user': user
            })

        if current_password and not user.user.check_password(current_password):
            return render(request, 'base/edit_profile.html', {
                'error': "Contraseña actual incorrecta.",
                'user': user
            })

        if first_name:
            user.user.first_name = first_name
        if last_name:
            user.user.last_name = last_name

        if new_email:
            if User.objects.filter(email=new_email).exclude(id=user.user.id).exists():
                return render(request, 'base/edit_profile.html', {
                    'error': "El nuevo correo electrónico ya está registrado.",
                    'user': user
                })
            user.user.email = new_email
            user.user.username = new_email

        if new_password or repeat_password:
            if not new_password or not repeat_password:
                return render(request, 'base/edit_profile.html', {
                    'error': "Debe completar ambos campos de la nueva contraseña.",
                    'user': user
                })
            if new_password != repeat_password:
                return render(request, 'base/edit_profile.html', {
                    'error': "Las nuevas contraseñas no coinciden.",
                    'user': user
                })
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
