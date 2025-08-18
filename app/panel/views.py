from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.urls import reverse

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
        return render(request, 'panel/list_users.html', context)

    else:
        return render(request, 'panel/list_users.html', {'error': 'Invalid request method'})


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
            return render(request, 'panel/list_users.html', {'error': 'Usuario no encontrado'})
    else:
        return render(request, 'panel/list_users.html', {'error': 'Invalid request method'})
