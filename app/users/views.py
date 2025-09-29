    # Create your views here.
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
import logging
from app.users.models import UserBase
logger = logging.getLogger(__name__)




def edit_user_view(request):
    logger.info("Acceso a edit_user_view por usuario: %s", request.user)
    if not request.user.is_authenticated:
        logger.warning("Usuario no autenticado en edit_user_view")
        return redirect(f"{reverse('login')}?next={request.path}")

    try:
        user = UserBase.objects.get(user=request.user)
    except UserBase.DoesNotExist:
        logger.error("UserBase no encontrado para usuario: %s", request.user)
        return redirect(reverse('home'))

    if request.method == 'POST':
        logger.debug("POST recibido en edit_user_view")
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        profile_photo = request.FILES.get('profile_image')
        if profile_photo:
            user.profile_photo = profile_photo
            logger.info("Foto de perfil actualizada para usuario: %s", request.user)
        if first_name:
            user.user.first_name = first_name
            logger.info("Nombre actualizado para usuario: %s", request.user)
        if last_name:
            user.user.last_name = last_name
            logger.info("Apellido actualizado para usuario: %s", request.user)
        user.save()
        user.user.save()
        messages.success(request, "Perfil actualizado correctamente.")
        logger.info("Perfil actualizado correctamente para usuario: %s", request.user)
        return redirect(reverse('home'))

    return render(request, 'base/edit_profile.html', {'user': user})
