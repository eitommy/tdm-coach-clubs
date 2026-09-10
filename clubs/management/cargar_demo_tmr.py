import os
from datetime import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from asistencia.models import Jugador
from clubs.models import Club, PerfilUsuario, TurnoClub


class Command(BaseCommand):
    help = "Crea o actualiza los datos mínimos de demo de TMR en Render."

    @transaction.atomic
    def handle(self, *args, **options):
        admin_password = os.environ.get(
            "DEMO_ADMIN_PASSWORD",
            "TmrDemo2026!",
        )
        trainer_password = os.environ.get(
            "DEMO_TRAINER_PASSWORD",
            "TmrDemo2026!",
        )

        club, _ = Club.objects.get_or_create(
            nombre="Tmr",
            defaults={
                "activo": True,
            },
        )

        if not club.activo:
            club.activo = True
            club.save(
                update_fields=["activo"],
            )

        admin, _ = User.objects.get_or_create(
            username="matias_tmr",
        )
        admin.first_name = "Matias"
        admin.last_name = "Pighini"
        admin.is_active = True
        admin.set_password(admin_password)
        admin.save()

        PerfilUsuario.objects.update_or_create(
            usuario=admin,
            defaults={
                "club": club,
                "rol": PerfilUsuario.Rol.ADMIN,
                "activo": True,
            },
        )

        entrenador, _ = User.objects.get_or_create(
            username="Chapa",
        )
        entrenador.is_active = True
        entrenador.set_password(trainer_password)
        entrenador.save()

        PerfilUsuario.objects.update_or_create(
            usuario=entrenador,
            defaults={
                "club": club,
                "rol": PerfilUsuario.Rol.ENTRENADOR,
                "activo": True,
            },
        )

        TurnoClub.objects.update_or_create(
            club=club,
            dia_semana=0,
            orden=1,
            defaults={
                "nombre": "Turno 1",
                "hora_inicio": time(15, 0),
                "hora_fin": time(17, 0),
                "activo": True,
            },
        )

        Jugador.objects.update_or_create(
            club=club,
            nombre="Lautaro",
            apellido="Luzzi",
            defaults={
                "activo": True,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo TMR lista: club, admin, entrenador, turno y jugador."
            )
        )
