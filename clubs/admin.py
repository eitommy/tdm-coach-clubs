from django.contrib import admin

from .models import Club, PerfilUsuario, TurnoClub


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "email",
        "telefono",
        "activo",
        "creado",
    )

    search_fields = (
        "nombre",
        "email",
    )

    list_filter = (
        "activo",
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "club",
        "rol",
        "activo",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "club__nombre",
    )

    list_filter = (
        "club",
        "rol",
        "activo",
    )


@admin.register(TurnoClub)
class TurnoClubAdmin(admin.ModelAdmin):
    list_display = (
        "club",
        "dia_semana",
        "nombre",
        "hora_inicio",
        "hora_fin",
        "orden",
        "activo",
    )

    search_fields = (
        "club__nombre",
        "nombre",
    )

    list_filter = (
        "club",
        "dia_semana",
        "activo",
    )

    ordering = (
        "club",
        "dia_semana",
        "orden",
    )