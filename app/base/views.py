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
import logging
logger = logging.getLogger(__name__)

import socket
from smtplib import SMTPException, SMTPAuthenticationError, SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError
from django.core.mail import BadHeaderError

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

        # Bloque 1: Creación de usuario y userbase
        try:
            user = User.objects.create_user(username=email, email=email, password=password,
                                            first_name=first_name, last_name=last_name, is_active=False)
            logger.info(f"Usuario creado: {email}")
            userbase = UserBase.objects.create(user=user)
            userbase.save()
            logger.info(f"UserBase creado para: {email}")
            code = userbase.generate_auth_code()
            logger.info(f"Código de verificación generado para: {email}")
        except Exception as e:
            logger.exception(f"Error crítico creando usuario {email}: {e}")
            return render(request, 'base/register_user.html', {'error': "Error al crear la cuenta. Por favor, intente nuevamente."})

        # Bloque 2: Envío de correo
        verification_link = request.build_absolute_uri(
            reverse("base:verify_email") + f"?code={code}"
        )

        # Verificar configuración de email
        if not settings.EMAIL_HOST_PASSWORD:
            logger.error(f"EMAIL_HOST_PASSWORD no está configurado. No se puede enviar correo a {email}")
            return render(request, 'base/register_user.html', {'error': "El sistema de correo no está configurado correctamente. Contacte al administrador."})

        try:
            logger.info(f"Enviando correo de verificación a: {email}")
            result = send_mail(
                subject="Verifica tu cuenta",
                message=f"Hola {first_name},\n\nPor favor verifica tu cuenta haciendo clic en el siguiente enlace:\n{verification_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"✅ Correo enviado exitosamente a: {email}. Resultado: {result}")
        except BadHeaderError as e:
            logger.error(f"❌ BadHeaderError al enviar correo a {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "Error en el encabezado del correo."})
        except SMTPAuthenticationError as e:
            logger.error(f"❌ SMTPAuthenticationError para {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "Error de autenticación con el servidor de correo."})
        except SMTPSenderRefused as e:
            logger.error(f"❌ SMTPSenderRefused para {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "El servidor rechazó el remitente del correo."})
        except SMTPRecipientsRefused as e:
            logger.error(f"❌ SMTPRecipientsRefused para {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "El servidor rechazó el destinatario."})
        except SMTPDataError as e:
            logger.error(f"❌ SMTPDataError para {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "Error en los datos del correo."})
        except SMTPException as e:
            logger.error(f"❌ SMTPException al enviar correo a {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "Error del servidor de correo. Intente nuevamente más tarde."})
        except socket.error as e:
            logger.error(f"❌ socket.error al enviar correo a {email}: {str(e)}", exc_info=True)
            return render(request, 'base/register_user.html', {'error': "No se pudo conectar al servidor de correo."})
        except Exception as e:
            logger.exception(f"❌ Error INESPERADO enviando correo a {email}: {str(e)}")
            return render(request, 'base/register_user.html', {'error': "Error inesperado al enviar el correo. Por favor, contacte al administrador."})

        logger.info(f"✅ Registro completado exitosamente para: {email}")
        return redirect(reverse('base:verification_mail_sent'))

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
            user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
            logger.info(f"Usuario de escuela creado: {email}")

            # Crear UserBase para la escuela (estaba faltando)
            userbase = UserBase.objects.create(user=user)
            userbase.save()
            logger.info(f"UserBase creado para escuela: {email}")

            slug = slugify(name)
            school = School.objects.create(user=user, name=name, slug=slug)
            school.email_verified = False
            school.save()
            logger.info(f"Escuela creada: {name}")

            code = userbase.generate_auth_code()

            verification_link = request.build_absolute_uri(
                reverse("base:verify_email") + f"?code={code}"
            )

            # Verificar que la configuración de email esté completa
            if not settings.EMAIL_HOST_PASSWORD:
                logger.error("EMAIL_HOST_PASSWORD no está configurado")
                return render(request, 'base/register_school.html', {'error': "El sistema de correo no está configurado correctamente. Contacte al administrador."})

            try:
                logger.info(f"Enviando correo de verificación a escuela: {email}")
                result = send_mail(
                    subject="DondeEstudiar - Verifica tu escuela",
                    message=f"Hola {name},\n\nPor favor verifica tu cuenta haciendo clic en el siguiente enlace:\n{verification_link}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                logger.info(f"Correo de verificación enviado a escuela: {email}. Resultado: {result}")
            except BadHeaderError as e:
                logger.error(f"Header inválido al enviar correo a escuela {email}: {e}")
                return render(request, 'base/register_school.html', {'error': "Error en el encabezado del correo."})
            except (SMTPAuthenticationError, SMTPSenderRefused) as e:
                logger.error(f"Autenticación/Remitente rechazado para escuela {email}: {e}")
                return render(request, 'base/register_school.html', {'error': "Error de autenticación con el servidor de correo."})
            except (SMTPRecipientsRefused, SMTPDataError) as e:
                logger.error(f"Servidor SMTP rechazó destinatario/datos para escuela {email}: {e}")
                return render(request, 'base/register_school.html', {'error': "El servidor de correo rechazó el envío."})
            except (SMTPException, socket.error) as e:
                logger.error(f"Error de conexión SMTP al enviar correo a escuela {email}: {e}")
                return render(request, 'base/register_school.html', {'error': "No se pudo enviar el correo. Intente nuevamente más tarde."})
            except Exception as e:
                logger.exception(f"Error inesperado enviando correo a escuela {email}: {e}")
                return render(request, 'base/register_school.html', {'error': "Error inesperado al enviar el correo."})

            return redirect(reverse('base:verification_mail_sent'))

        except Exception as e:
            logger.exception(f"Error crítico durante registro de escuela {email}: {e}")
            return render(request, 'base/register_school.html', {'error': "Error al crear la cuenta. Por favor, intente nuevamente."})

    else:
        messages.add_message(request, messages.INFO, 'Por favor, regístrese para continuar.')
        logger.info("Acceso a registro de escuela por método no soportado")
        return redirect('users:register_school')


def verify_email(request):
    code = request.GET.get("code")
    logger.info(f"Intento de verificación de email con código: {code}")
    if not code:
        logger.warning("Verificación fallida: código no proporcionado")
        return render(request, "base/verify_email.html", {"error": "Código inválido."})

    try:
        userbase = UserBase.objects.get(recovery_code=code)
    except UserBase.DoesNotExist:
        logger.warning(f"Verificación fallida: código inválido o expirado ({code})")
        return render(request, "base/verify_email.html", {"error": "Código inválido o expirado."})
    logger.info(f"Email verificado para usuario: {userbase.user.email}")

    userbase.email_verified = True
    userbase.recovery_code = None
    userbase.user.is_active = True
    userbase.user.save()
    userbase.save()

    messages.success(request, "Tu cuenta ha sido verificada. Ahora puedes iniciar sesión.")
    return redirect("login")


def verification_mail_sent(request):
    logger.info("Vista de correo de verificación enviado mostrada")
    return render(request, 'base/verify_email_sent.html')
