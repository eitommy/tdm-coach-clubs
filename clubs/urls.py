from django.urls import path

from . import views


urlpatterns = [
    path(
        "configuracion/",
        views.configuracion_club,
        name="configuracion_club",
    ),

    path(
        "turnos/",
        views.lista_turnos,
        name="lista_turnos",
    ),

    path(
        "turnos/nuevo/",
        views.crear_turno,
        name="crear_turno",
    ),

    path(
        "turnos/<int:turno_id>/editar/",
        views.editar_turno,
        name="editar_turno",
    ),

    path(
        "turnos/<int:turno_id>/eliminar/",
        views.eliminar_turno,
        name="eliminar_turno",
    ),

    path(
        "usuarios/",
        views.lista_usuarios,
        name="lista_usuarios",
    ),

    path(
        "usuarios/nuevo/",
        views.crear_usuario,
        name="crear_usuario",
    ),

    path(
        "usuarios/<int:perfil_id>/editar/",
        views.editar_usuario,
        name="editar_usuario",
    ),

    path(
        "usuarios/<int:perfil_id>/estado/",
        views.cambiar_estado_usuario,
        name="cambiar_estado_usuario",
    ),
]