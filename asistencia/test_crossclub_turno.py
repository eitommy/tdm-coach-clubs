from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub
from asistencia.models import Entrenamiento


class SeguridadCrossClubAccionesTurnoTests(TestCase):
    def setUp(self):
        self.club_a = Club.objects.create(
            nombre="Club A",
        )

        self.club_b = Club.objects.create(
            nombre="Club B",
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
            hora_inicio=time(18, 0),
            hora_fin=time(20, 0),
            orden=1,
            activo=True,
        )

        self.usuario_a = User.objects.create_user(
            username="usuario_a",
            password="TestPass123!",
        )

        self.usuario_b = User.objects.create_user(
            username="usuario_b",
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

        self.entrenamiento_a = Entrenamiento.objects.create(
            club=self.club_a,
            fecha=date(2026, 8, 31),
            turno_config=self.turno_a,
            responsable_usuario=self.usuario_a,
        )

        self.entrenamiento_b = Entrenamiento.objects.create(
            club=self.club_b,
            fecha=date(2026, 8, 31),
            turno_config=self.turno_b,
            responsable_usuario=self.usuario_b,
        )

    def test_no_puede_tomar_turno_de_otro_club(self):
        self.entrenamiento_b.responsable_usuario = None
        self.entrenamiento_b.save(
            update_fields=["responsable_usuario"],
        )

        self.client.force_login(self.usuario_a)

        response = self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento_b.id],
            )
        )

        self.entrenamiento_b.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(
            self.entrenamiento_b.responsable_usuario,
        )

    def test_no_puede_finalizar_turno_de_otro_club(self):
        self.client.force_login(self.usuario_a)

        response = self.client.post(
            reverse(
                "finalizar_turno",
                args=[self.entrenamiento_b.id],
            )
        )

        self.entrenamiento_b.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            self.entrenamiento_b.finalizado,
        )

    def test_no_puede_reabrir_turno_de_otro_club(self):
        self.entrenamiento_b.finalizado = True
        self.entrenamiento_b.finalizado_por = self.usuario_b
        self.entrenamiento_b.save(
            update_fields=[
                "finalizado",
                "finalizado_por",
            ]
        )

        self.client.force_login(self.usuario_a)

        response = self.client.post(
            reverse(
                "reabrir_turno",
                args=[self.entrenamiento_b.id],
            )
        )

        self.entrenamiento_b.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            self.entrenamiento_b.finalizado,
        )

    def test_usuario_del_club_correcto_no_recibe_404(self):
        self.client.force_login(self.usuario_a)

        response = self.client.post(
            reverse(
                "tomar_turno",
                args=[self.entrenamiento_a.id],
            )
        )

        self.assertNotEqual(
            response.status_code,
            404,
        )
