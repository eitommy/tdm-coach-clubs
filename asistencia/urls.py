from django.urls import include, path
from . import views


urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("", views.inicio, name="inicio"),
    path("acerca/", views.acerca, name="acerca"),
    path("perfil/", views.perfil, name="perfil"),

    path(
        "ir-a-fecha-asistencia/",
        views.ir_a_fecha_asistencia,
        name="ir_a_fecha_asistencia",
    ),

    path(
        "dia/<str:fecha_str>/turno/<int:turno_id>/",
        views.dia_turno,
        name="dia_turno",
    ),

    path(
        "dia/<str:fecha_str>/turno/<int:turno_id>/copiar-jugadores/",
        views.copiar_jugadores_turno,
        name="copiar_jugadores_turno",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/guardar-info/",
        views.guardar_info_entrenamiento,
        name="guardar_info_entrenamiento",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/no-entrenamiento/",
        views.guardar_no_entrenamiento,
        name="guardar_no_entrenamiento",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/tomar-turno/",
        views.tomar_turno,
        name="tomar_turno",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/agregar-jugador/",
        views.agregar_jugador,
        name="agregar_jugador",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/agregar-trabajo/",
        views.agregar_trabajo_turno,
        name="agregar_trabajo_turno",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/copiar-ayer/",
        views.copiar_lista_ayer,
        name="copiar_lista_ayer",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/todos-asistieron/",
        views.marcar_todos_asistieron,
        name="marcar_todos_asistieron",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/partido/nuevo/",
        views.crear_partido_turno,
        name="crear_partido_turno",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/finalizar/",
        views.finalizar_turno,
        name="finalizar_turno",
    ),

    path(
        "entrenamiento/<int:entrenamiento_id>/reabrir/",
        views.reabrir_turno,
        name="reabrir_turno",
    ),

    path(
        "asistencia/<int:asistencia_id>/quitar/",
        views.quitar_jugador,
        name="quitar_jugador",
    ),

    path(
        "asistencia/<int:asistencia_id>/estado/",
        views.cambiar_estado,
        name="cambiar_estado",
    ),

    path(
        "asistencia/<int:asistencia_id>/observacion/",
        views.guardar_observacion_jugador,
        name="guardar_observacion_jugador",
    ),

    path(
        "asistencia/<int:asistencia_id>/motivo-ausencia/",
        views.guardar_motivo_ausencia,
        name="guardar_motivo_ausencia",
    ),

    path("jugadores/", views.lista_jugadores, name="lista_jugadores"),
    path("jugadores/nuevo/", views.crear_jugador, name="crear_jugador"),

    path(
        "jugadores/<int:pk>/editar/",
        views.editar_jugador,
        name="editar_jugador",
    ),

    path(
        "jugadores/<int:jugador_id>/historial/",
        views.historial_jugador,
        name="historial_jugador",
    ),

    path("ejercicios/", views.lista_ejercicios, name="lista_ejercicios"),
    path("ejercicios/nuevo/", views.crear_ejercicio, name="crear_ejercicio"),

    path(
        "ejercicios/<int:pk>/editar/",
        views.editar_ejercicio,
        name="editar_ejercicio",
    ),

    path(
        "ejercicios/categorias/",
        views.lista_categorias_ejercicio,
        name="lista_categorias_ejercicio",
    ),

    path(
        "ejercicios/categorias/nueva/",
        views.crear_categoria_ejercicio,
        name="crear_categoria_ejercicio",
    ),

    path(
        "ejercicios/categorias/<int:pk>/editar/",
        views.editar_categoria_ejercicio,
        name="editar_categoria_ejercicio",
    ),

    path(
        "ejercicios/cargar/",
        views.cargar_ejercicios,
        name="cargar_ejercicios",
    ),

    path(
        "ejercicios/guardar/",
        views.guardar_ejercicios,
        name="guardar_ejercicios",
    ),

    path(
        "trabajo-turno/<int:trabajo_id>/editar/",
        views.editar_trabajo_turno,
        name="editar_trabajo_turno",
    ),

    path(
        "trabajo-turno/<int:trabajo_id>/eliminar/",
        views.eliminar_trabajo_turno,
        name="eliminar_trabajo_turno",
    ),

    path(
        "observacion/<int:observacion_id>/editar/",
        views.editar_observacion_jugador,
        name="editar_observacion_jugador",
    ),

    path(
        "observacion/<int:observacion_id>/eliminar/",
        views.eliminar_observacion_jugador,
        name="eliminar_observacion_jugador",
    ),

    path(
        "partido/<int:partido_id>/editar/",
        views.editar_partido_turno,
        name="editar_partido_turno",
    ),

    path(
        "partido/<int:partido_id>/eliminar/",
        views.eliminar_partido_turno,
        name="eliminar_partido_turno",
    ),

    path(
        "seguimiento-semanal/",
        views.seguimiento_semanal,
        name="seguimiento_semanal",
    ),

    path("reportes/", views.reportes, name="reportes"),

    path(
        "reportes/exportar-excel/",
        views.exportar_reporte_mensual,
        name="exportar_reporte_mensual",
    ),

    path(
        "dashboard-mensual/",
        views.dashboard_mensual,
        name="dashboard_mensual",
    ),

    path(
        "resumen-dia/",
        views.resumen_dia,
        name="resumen_dia",
    ),
]
