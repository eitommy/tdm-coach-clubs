from .utils import obtener_perfil_usuario


def club_actual(request):
    """
    Hace disponible información del club y del rol del usuario
    en todos los templates.

    Variables disponibles:
    - club_actual
    - perfil_club
    - es_admin_club
    """

    if not request.user.is_authenticated:
        return {
            "club_actual": None,
            "perfil_club": None,
            "es_admin_club": False,
        }

    perfil = obtener_perfil_usuario(
        request.user
    )

    if perfil is None:
        return {
            "club_actual": None,
            "perfil_club": None,
            "es_admin_club": False,
        }

    return {
        "club_actual": perfil.club,
        "perfil_club": perfil,
        "es_admin_club": (
            perfil.activo
            and perfil.club.activo
            and perfil.rol == "admin"
        ),
    }