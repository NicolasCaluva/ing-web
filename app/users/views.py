from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.

def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    if request.method == 'POST':
        if email and password:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user.check_password(password):
                    pass
                return render(request, 'school/school_list.html', {'user': user})
            else:
                return render(request, 'base/login.html',
                              {'error': "El correo electrónico o la contraseña son incorrectos."})
        else:
            error_message = "Por favor, ingrese su correo electrónico y contraseña."
            return render(request, 'base/login.html', {'error': error_message})

    return redirect('usuarios:login', {'error': 'Acción no permitida'})
