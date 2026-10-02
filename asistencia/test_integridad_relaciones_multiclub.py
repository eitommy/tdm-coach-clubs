from datetime import time

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from clubs.models import Club, PerfilUsuario, TurnoClub
from asistencia.models import CategoriaEjercicio, Ejercicio, Entrenamiento


class IntegridadRelacionesMulticlubTests(TestCase):
    def setUp(self):
        self.club_a = Club.objects.create(nombre="Club A")
        self.club_b = Club.objects.create(nombre="Club B")

        self.usuario_a = User.objects.create_user(
            username="usuario_a_integridad",
            password="TestPass123!",
        )
        self.usuario_b = User.objects.create_user(
            username="usuario_b_integridad",
            password="TestPass123!",
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_a,
            club=self.club_a,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )
        PerfilUsuario.objects.create(
            usuario=self.usuario_b,
            club=self.club_b,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.turno_a = TurnoClub.objects.create(
            club=self.club_a,
            dia_semana=0,
            nombre="Turno A",
            hora_inicio=time(15, 0),
            hora_fin=time(17, 0),
            orden=1,
            activo=True,
        )
        self.turno_b = TurnoClub.objects.create(
            club=self.club_b,
            dia_semana=0,
            nombre="Turno B",
            hora_inicio=time(15, 0),
            hora_fin=time(17, 0),
            orden=1,
            activo=True,
        )

        self.categoria_a = CategoriaEjercicio.objects.create(
            club=self.club_a,
            nombre="Categoría A",
            orden=1,
            activo=True,
        )
        self.categoria_b = CategoriaEjercicio.objects.create(
            club=self.club_b,
            nombre="Categoría B",
            orden=1,
            activo=True,
        )

    def test_ejercicio_rechaza_categoria_de_otro_club(self):
        ejercicio = Ejercicio(
            club=self.club_a,
            categoria_config=self.categoria_b,
            nombre="Ejercicio cruzado",
            activo=True,
        )

        with self.assertRaises(ValidationError) as contexto:
            ejercicio.full_clean()

        self.assertIn(
            "categoria_config",
            contexto.exception.message_dict,
        )

    def test_entrenamiento_rechaza_turno_de_otro_club(self):
        entrenamiento = Entrenamiento(
            club=self.club_a,
            fecha=timezone.localdate(),
            turno_config=self.turno_b,
        )

        with self.assertRaises(ValidationError) as contexto:
            entrenamiento.full_clean()

        self.assertIn(
            "turno_config",
            contexto.exception.message_dict,
        )

    def test_entrenamiento_rechaza_responsable_de_otro_club(self):
        entrenamiento = Entrenamiento(
            club=self.club_a,
            fecha=timezone.localdate(),
            turno_config=self.turno_a,
            responsable_usuario=self.usuario_b,
        )

        with self.assertRaises(ValidationError) as contexto:
            entrenamiento.full_clean()

        self.assertIn(
            "responsable_usuario",
            contexto.exception.message_dict,
        )

    def test_relaciones_del_mismo_club_son_validas(self):
        ejercicio = Ejercicio(
            club=self.club_a,
            categoria_config=self.categoria_a,
            nombre="Ejercicio válido",
            activo=True,
        )
        ejercicio.full_clean()

        entrenamiento = Entrenamiento(
            club=self.club_a,
            fecha=timezone.localdate(),
            turno_config=self.turno_a,
            responsable_usuario=self.usuario_a,
        )
        entrenamiento.full_clean()
