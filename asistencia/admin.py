from django.contrib import admin

from .models import (
    Asistencia,
    Ejercicio,
    EjercicioRealizado,
    EjercicioTurno,
    Entrenamiento,
    Entrenador,
    Jugador,
    ObservacionJugador,
    PartidoTurno,
    SetPartido,
    TrabajoTurno,
)


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "club", "activo")
    list_filter = ("club", "activo")
    search_fields = ("nombre", "apellido")


@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "club")
    list_filter = ("club",)


@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "turno_config",
        "club",
        "responsable_usuario",
        "finalizado",
        "no_se_entreno",
    )
    list_filter = (
        "club",
        "turno_config",
        "fecha",
        "finalizado",
        "no_se_entreno",
    )
    search_fields = (
        "turno_config__nombre",
        "responsable_usuario__username",
        "responsable_usuario__first_name",
        "responsable_usuario__last_name",
    )
    list_select_related = (
        "club",
        "turno_config",
        "responsable_usuario",
    )
    ordering = (
        "-fecha",
        "turno_config__orden",
    )


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "entrenamiento",
        "estado",
    )
    list_filter = (
        "estado",
        "entrenamiento__club",
        "entrenamiento__turno_config",
        "entrenamiento__fecha",
    )
    search_fields = (
        "jugador__nombre",
        "jugador__apellido",
        "entrenamiento__turno_config__nombre",
    )
    list_select_related = (
        "jugador",
        "entrenamiento",
        "entrenamiento__club",
        "entrenamiento__turno_config",
    )


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "club",
        "activo",
    )
    list_filter = (
        "club",
        "categoria",
        "activo",
    )
    search_fields = ("nombre",)


@admin.register(EjercicioTurno)
class EjercicioTurnoAdmin(admin.ModelAdmin):
    list_display = ("entrenamiento", "ejercicio")
    list_filter = (
        "entrenamiento__club",
        "entrenamiento__turno_config",
        "ejercicio__categoria",
    )


@admin.register(TrabajoTurno)
class TrabajoTurnoAdmin(admin.ModelAdmin):
    list_display = (
        "entrenamiento",
        "cambio",
        "tipo",
        "jugador_1",
        "jugador_2",
    )
    list_filter = (
        "entrenamiento__club",
        "entrenamiento__turno_config",
        "tipo",
    )


@admin.register(ObservacionJugador)
class ObservacionJugadorAdmin(admin.ModelAdmin):
    list_display = (
        "jugador",
        "entrenamiento",
        "creada_el",
        "creada_por",
    )
    list_filter = (
        "entrenamiento__club",
        "entrenamiento__turno_config",
    )
    search_fields = (
        "jugador__nombre",
        "jugador__apellido",
        "texto",
    )


@admin.register(PartidoTurno)
class PartidoTurnoAdmin(admin.ModelAdmin):
    list_display = (
        "entrenamiento",
        "jugador_1",
        "jugador_2",
    )
    list_filter = (
        "entrenamiento__club",
        "entrenamiento__turno_config",
    )


@admin.register(SetPartido)
class SetPartidoAdmin(admin.ModelAdmin):
    list_display = (
        "partido",
        "numero",
        "puntos_jugador_1",
        "puntos_jugador_2",
    )


@admin.register(EjercicioRealizado)
class EjercicioRealizadoAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
