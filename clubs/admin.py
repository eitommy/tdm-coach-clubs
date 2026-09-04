from django.contrib import admin

from .models import Club


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