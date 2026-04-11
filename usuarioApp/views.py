from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from rest_framework import permissions, viewsets

from .models import EncargadoBiblioteca, usuario
from .serializers import EncargadoBibliotecaSerializer, UsuarioSerializer


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_landing_url(request.user))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            login(request, user)
            if user.is_superuser:
                messages.success(request, 'Inicio de sesión exitoso: perfil administrador.')
            elif hasattr(user, 'encargado'):
                messages.success(request, 'Inicio de sesión exitoso: perfil encargado.')
            else:
                logout(request)
                messages.error(
                    request,
                    'Tu cuenta no tiene un rol válido para ingresar al sistema.',
                )
                return redirect('login')

            return redirect(_landing_url(user))

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


def _landing_url(user):
    return 'encargados_ui' if user.is_superuser else 'dashboard'


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = usuario.objects.all()
    serializer_class = UsuarioSerializer

    @staticmethod
    @login_required(login_url='login')
    def usuarios_view(request):
        return render(request, 'usuarios.html')


class EncargadoBibliotecaViewSet(viewsets.ModelViewSet):
    queryset = EncargadoBiblioteca.objects.all()
    serializer_class = EncargadoBibliotecaSerializer
    permission_classes = [permissions.IsAdminUser]

    @staticmethod
    @user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
    def encargados_view(request):
        return render(request, 'encargados.html')