from datetime import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from asistencia.models import Entrenamiento, Jugador
from clubs.models import Club, PerfilUsuario, TurnoClub


CLUB_NOMBRE = "QA Carga Diaria"
ADMIN_USERNAME = "qa_carga_admin"
ENTRENADOR_USERNAME = "qa_carga_entrenador"
PASSWORD = "Prueba12345!"


class Command(BaseCommand):
    help = (
        "Prepara un club temporal para probar los estados vacíos "
        "de la pantalla de carga diaria."
    )

    ESTADOS = (
        "sin_turnos",
        "sin_jugadores",
        "sin_entrenadores",
        "sin_ejercicios",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--estado",
            required=True,
            choices=self.ESTADOS,
            help="Estado que se quiere probar.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        estado = options["estado"]

        club_existente = Club.objects.filter(nombre=CLUB_NOMBRE).first()

        if club_existente:
            Entrenamiento.objects.filter(club=club_existente).delete()
            club_existente.delete()

        User.objects.filter(
            username__in=[ADMIN_USERNAME, ENTRENADOR_USERNAME]
        ).delete()

        club = Club.objects.create(
            nombre=CLUB_NOMBRE,
            color_primario="#2563EB",
            color_secundario="#111827",
            activo=True,
        )

        admin = User.objects.create_user(
            username=ADMIN_USERNAME,
            password=PASSWORD,
            first_name="Admin",
            last_name="QA",
            email="qa-admin@example.com",
        )

        PerfilUsuario.objects.create(
            usuario=admin,
            club=club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        if estado == "sin_turnos":
            self._mostrar_resultado(estado)
            return

        for dia in range(7):
            TurnoClub.objects.create(
                club=club,
                dia_semana=dia,
                nombre="Turno prueba",
                hora_inicio=time(18, 0),
                hora_fin=time(20, 0),
                orden=1,
                activo=True,
            )

        if estado == "sin_jugadores":
            self._crear_entrenador(club)
            self._mostrar_resultado(estado)
            return

        if estado == "sin_entrenadores":
            self._crear_jugador(club)
            self._mostrar_resultado(estado)
            return

        if estado == "sin_ejercicios":
            self._crear_jugador(club)
            self._crear_entrenador(club)
            self._mostrar_resultado(estado)
            return

        raise CommandError("Estado de prueba no reconocido.")

    def _crear_jugador(self, club):
        Jugador.objects.create(
            club=club,
            nombre="Jugador",
            apellido="Prueba",
            activo=True,
        )

    def _crear_entrenador(self, club):
        entrenador = User.objects.create_user(
            username=ENTRENADOR_USERNAME,
            password=PASSWORD,
            first_name="Entrenador",
            last_name="QA",
            email="qa-entrenador@example.com",
        )

        PerfilUsuario.objects.create(
            usuario=entrenador,
            club=club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

    def _mostrar_resultado(self, estado):
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f'Club temporal "{CLUB_NOMBRE}" preparado.'
            )
        )
        self.stdout.write(f"Estado: {estado}")
        self.stdout.write("")
        self.stdout.write("Ingresá con:")
        self.stdout.write(f"  usuario: {ADMIN_USERNAME}")
        self.stdout.write(f"  contraseña: {PASSWORD}")
        self.stdout.write("")
        self.stdout.write(
            "Cuando termines, ejecutá: "
            "python manage.py eliminar_club_prueba_carga"
        )
