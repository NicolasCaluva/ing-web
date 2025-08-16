from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        return redirect('school:school_list')

    if request.method == 'GET':
        return render(request, 'base/login.html')

    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                return render(request, 'school/school_list.html', {'user': user})
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
    return redirect('users:login')
