from datetime import time

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from asistencia.models import CategoriaEjercicio, Ejercicio, Entrenamiento, Jugador
from clubs.models import Club, PerfilUsuario, TurnoClub


class LimpiarDatosPruebaTMRTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(nombre="TMR", activo=True)
        self.usuario = User.objects.create_user(
            username="matias_tmr",
            password="ClaveSegura2026!",
        )
        self.perfil = PerfilUsuario.objects.create(
            usuario=self.usuario,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )
        self.turno = TurnoClub.objects.create(
            club=self.club,
            dia_semana=0,
            nombre="Turno 1",
            hora_inicio=time(15, 0),
            hora_fin=time(17, 0),
            orden=1,
            activo=True,
        )
        self.jugador = Jugador.objects.create(
            club=self.club,
            nombre="Lautaro",
            apellido="Luzzi",
            activo=True,
        )
        self.categoria = CategoriaEjercicio.objects.create(
            club=self.club,
            nombre="Movilidad",
            orden=1,
            activo=True,
        )
        self.ejercicio = Ejercicio.objects.create(
            club=self.club,
            nombre="Ejercicio prueba",
            categoria_config=self.categoria,
            activo=True,
        )
        self.entrenamiento = Entrenamiento.objects.create(
            club=self.club,
            fecha="2026-09-14",
            turno_config=self.turno,
        )

    def test_requiere_confirmacion(self):
        with self.assertRaises(CommandError):
            call_command("limpiar_datos_prueba_tmr")

        self.assertTrue(Club.objects.filter(pk=self.club.pk).exists())
        self.assertTrue(
            Entrenamiento.objects.filter(pk=self.entrenamiento.pk).exists()
        )

    def test_limpia_operativos_y_conserva_club_y_usuario(self):
        call_command("limpiar_datos_prueba_tmr", confirmar=True)

        self.assertTrue(Club.objects.filter(pk=self.club.pk).exists())
        self.assertTrue(User.objects.filter(pk=self.usuario.pk).exists())
        self.assertTrue(PerfilUsuario.objects.filter(pk=self.perfil.pk).exists())
        self.assertFalse(Entrenamiento.objects.filter(club=self.club).exists())
        self.assertFalse(Ejercicio.objects.filter(club=self.club).exists())
        self.assertFalse(CategoriaEjercicio.objects.filter(club=self.club).exists())
        self.assertFalse(Jugador.objects.filter(club=self.club).exists())
        self.assertFalse(TurnoClub.objects.filter(club=self.club).exists())
