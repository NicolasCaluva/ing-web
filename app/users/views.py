    # Create your views here.
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from app.users.models import UserBase


def edit_user_view(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

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
