from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Club, InvitacionClub, PerfilUsuario, TurnoClub


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "estado_pago",
        "pagado_hasta",
        "email",
        "telefono",
        "activo",
        "creado",
    )

    list_filter = (
        "activo",
        "estado_pago",
    )

    search_fields = (
        "nombre",
        "email",
        "telefono",
    )

    readonly_fields = (
        "creado",
    )

    fieldsets = (
        (
            "Club",
            {
                "fields": (
                    "nombre",
                    "logo",
                    "color_primario",
                    "color_secundario",
                    "email",
                    "telefono",
                    "direccion",
                    "activo",
                    "creado",
                )
            },
        ),
        (
            "Suscripción / pago",
            {
                "fields": (
                    "estado_pago",
                    "pagado_hasta",
                    "observacion_pago",
                )
            },
        ),
    )


@admin.register(InvitacionClub)
class InvitacionClubAdmin(admin.ModelAdmin):
    list_display = (
        "referencia",
        "estado",
        "creada",
        "usada_en",
        "club_creado",
    )

    list_filter = (
        "creada",
        "usada_en",
    )

    search_fields = (
        "referencia",
        "club_creado__nombre",
    )

    readonly_fields = (
        "token",
        "creada",
        "usada_en",
        "club_creado",
        "enlace_registro",
    )

    fields = (
        "referencia",
        "token",
        "enlace_registro",
        "creada",
        "usada_en",
        "club_creado",
    )

    @admin.display(description="Estado")
    def estado(self, obj):
        return "Usada" if obj.usada else "Disponible"

    @admin.display(description="Link de registro")
    def enlace_registro(self, obj):
        if not obj or not obj.pk:
            return "Guardá primero la invitación para generar el link."

        if obj.usada:
            return "Esta invitación ya fue utilizada."

        ruta = reverse(
            "registro_club_invitacion",
            kwargs={
                "token": obj.token,
            },
        )

        url = f"{settings.APP_BASE_URL}{ruta}"

        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            url,
            url,
        )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "club",
        "rol",
        "activo",
    )

    list_filter = (
        "rol",
        "activo",
        "club",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "usuario__email",
        "club__nombre",
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

    list_filter = (
        "club",
        "dia_semana",
        "activo",
    )

    search_fields = (
        "club__nombre",
        "nombre",
    )

    ordering = (
        "club",
        "dia_semana",
        "orden",
        "hora_inicio",
    )
