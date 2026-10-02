from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import PerfilUsuario


def obtener_perfil_usuario(user):
    """
    Devuelve el perfil de club del usuario logueado.

    Los superusuarios de Django pueden no tener PerfilUsuario porque
    están pensados para administrar el sistema desde /admin/.
    """
    if not user.is_authenticated:
        return None

    try:
        return user.perfil_club
    except PerfilUsuario.DoesNotExist:
        return None


def obtener_club_usuario(user):
    """
    Devuelve el club al que pertenece el usuario.

    Si el usuario no tiene un PerfilUsuario asociado, devuelve None.
    """
    perfil = obtener_perfil_usuario(user)

    if perfil is None:
        return None

    if not perfil.activo:
        return None

    if not perfil.club.activo:
        return None

    return perfil.club


def usuario_es_admin_club(user):
    """
    Indica si el usuario es administrador de su club.
    """
    perfil = obtener_perfil_usuario(user)

    if perfil is None:
        return False

    return (
        perfil.activo
        and perfil.club.activo
        and perfil.rol == PerfilUsuario.Rol.ADMIN
    )


def usuario_es_entrenador(user):
    """
    Indica si el usuario pertenece a un club y tiene rol entrenador.
    """
    perfil = obtener_perfil_usuario(user)

    if perfil is None:
        return False

    return (
        perfil.activo
        and perfil.club.activo
        and perfil.rol == PerfilUsuario.Rol.ENTRENADOR
    )


def requerir_club(view_func):
    """
    Decorador para vistas operativas disponibles para cualquier usuario
    comercial activo del club, tanto administrador como entrenador.
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        club = obtener_club_usuario(request.user)

        if club is None:
            messages.error(
                request,
                (
                    "Tu usuario no está asociado a un club activo. "
                    "Contactá al administrador."
                ),
            )

            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper


def requerir_admin_club(view_func):
    """
    Decorador para pantallas exclusivas del administrador del club.

    Por ejemplo:
    - configuración y branding del club
    - usuarios, entrenadores y roles
    - administración comercial/pagos
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        perfil = obtener_perfil_usuario(request.user)

        if perfil is None:
            raise PermissionDenied(
                "Tu usuario no pertenece a ningún club."
            )

        if not perfil.activo or not perfil.club.activo:
            raise PermissionDenied(
                "Tu usuario o club se encuentra inactivo."
            )

        if perfil.rol != PerfilUsuario.Rol.ADMIN:
            raise PermissionDenied(
                "No tenés permisos para acceder a esta sección."
            )

        return view_func(request, *args, **kwargs)

    return wrapper
