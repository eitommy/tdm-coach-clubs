from django.shortcuts import render
from django.urls import reverse

from .models import PerfilUsuario
from .utils import obtener_perfil_usuario


class BloqueoSuscripcionMiddleware:
    """
    Bloquea el uso operativo de TDM Coach cuando la suscripción
    de un club superó el período de gracia.

    Se mantienen disponibles:
    - autenticación
    - logout / cambio de contraseña
    - Django Admin
    - archivos estáticos y media
    - configuración del club para el administrador
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # -----------------------------------------------------
        # USUARIO NO LOGUEADO
        # -----------------------------------------------------

        if not request.user.is_authenticated:
            return self.get_response(request)

        # -----------------------------------------------------
        # SUPERUSUARIO TÉCNICO
        # -----------------------------------------------------

        # El administrador técnico nunca queda bloqueado.
        if request.user.is_superuser:
            return self.get_response(request)

        # -----------------------------------------------------
        # PERFIL DEL CLUB
        # -----------------------------------------------------

        perfil = obtener_perfil_usuario(
            request.user
        )

        if perfil is None:
            return self.get_response(request)

        if not perfil.activo:
            return self.get_response(request)

        club = perfil.club

        if not club.activo:
            return self.get_response(request)

        # -----------------------------------------------------
        # SUSCRIPCIÓN NO BLOQUEADA
        # -----------------------------------------------------

        if not club.suscripcion_bloqueada:
            return self.get_response(request)

        # -----------------------------------------------------
        # RUTAS QUE SIEMPRE QUEDAN DISPONIBLES
        # -----------------------------------------------------

        path = request.path

        rutas_publicas = (
            "/accounts/",
            "/admin/",
            "/static/",
            "/media/",
        )

        if path.startswith(rutas_publicas):
            return self.get_response(request)

        # -----------------------------------------------------
        # CONFIGURACIÓN DEL CLUB
        # -----------------------------------------------------

        # El administrador del club puede seguir entrando
        # a la configuración para consultar su suscripción.
        if (
            perfil.rol == PerfilUsuario.Rol.ADMIN
            and path == reverse(
                "configuracion_club"
            )
        ):
            return self.get_response(request)

        # -----------------------------------------------------
        # BLOQUEO
        # -----------------------------------------------------

        return render(
            request,
            "clubs/suscripcion_bloqueada.html",
            {
                "club": club,
                "perfil": perfil,
            },
            status=403,
        )