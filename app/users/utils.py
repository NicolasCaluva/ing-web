from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerificationCode

def send_verification_code(user):
    code = EmailVerificationCode.generate_code()
    expires_at = timezone.now() + timedelta(minutes=10)  # expira en 10 minutos
    EmailVerificationCode.objects.create(user=user, code=code, expires_at=expires_at)

    send_mail(
        subject="Tu código de verificación",
        message=f"Tu código de verificación es: {code}. Expira en 10 minutos.",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )
