from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub
from asistencia.models import Entrenamiento


class PermisosAccionesSensiblesTurnoTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Test",
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

        self.admin = User.objects.create_user(
            username="admin_turno",
            password="TestPass123!",
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_turno",
            password="TestPass123!",
        )

        self.inactivo = User.objects.create_user(
            username="inactivo_turno",
            password="TestPass123!",
        )

        PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.inactivo,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=False,
        )

        self.entrenamiento = Entrenamiento.objects.create(
            club=self.club,
            fecha=date(2026, 8, 31),
            turno_config=self.turno,
        )

    def test_entrenador_activo_puede_tomar_turno(self):
        self.client.force_login(self.entrenador)

        response = self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            self.entrenamiento.responsable_usuario,
            self.entrenador,
        )

    def test_usuario_con_perfil_inactivo_no_puede_tomar_turno(self):
        self.client.force_login(self.inactivo)

        self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertIsNone(
            self.entrenamiento.responsable_usuario,
        )

    def test_usuario_django_inactivo_no_puede_tomar_turno(self):
        self.entrenador.is_active = False
        self.entrenador.save(
            update_fields=["is_active"],
        )

        self.client.force_login(self.entrenador)

        self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertIsNone(
            self.entrenamiento.responsable_usuario,
        )

    def test_usuario_sin_perfil_no_puede_tomar_turno(self):
        usuario = User.objects.create_user(
            username="sin_perfil",
            password="TestPass123!",
        )

        self.client.force_login(usuario)

        self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertIsNone(
            self.entrenamiento.responsable_usuario,
        )

    def test_usuario_de_otro_club_no_puede_tomar_turno(self):
        otro_club = Club.objects.create(
            nombre="Otro Club",
        )

        usuario_otro = User.objects.create_user(
            username="otro_club",
            password="TestPass123!",
        )

        PerfilUsuario.objects.create(
            usuario=usuario_otro,
            club=otro_club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.client.force_login(usuario_otro)

        response = self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertIsNone(
            self.entrenamiento.responsable_usuario,
        )
