from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub
from asistencia.models import Asistencia, Entrenamiento, Jugador


class CicloFinalizarReabrirTurnoTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Ciclo",
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
            username="admin_ciclo",
            password="TestPass123!",
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_ciclo",
            password="TestPass123!",
        )

        self.inactivo = User.objects.create_user(
            username="inactivo_ciclo",
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

        self.jugador = Jugador.objects.create(
            club=self.club,
            nombre="Jugador",
            apellido="Prueba",
            activo=True,
        )

        self.entrenamiento = Entrenamiento.objects.create(
            club=self.club,
            fecha=date(2026, 8, 31),
            turno_config=self.turno,
            responsable_usuario=self.entrenador,
        )

        Asistencia.objects.create(
            entrenamiento=self.entrenamiento,
            jugador=self.jugador,
            estado="asistio",
        )

    def test_entrenador_activo_puede_finalizar_turno_valido(self):
        self.client.force_login(self.entrenador)

        response = self.client.post(
            reverse(
                "finalizar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.entrenamiento.finalizado)
        self.assertEqual(
            self.entrenamiento.finalizado_por,
            self.entrenador,
        )
        self.assertIsNotNone(
            self.entrenamiento.finalizado_el,
        )

    def test_admin_activo_puede_finalizar_turno_valido(self):
        self.entrenamiento.responsable_usuario = self.admin
        self.entrenamiento.save(
            update_fields=["responsable_usuario"],
        )

        self.client.force_login(self.admin)

        self.client.post(
            reverse(
                "finalizar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertTrue(self.entrenamiento.finalizado)
        self.assertEqual(
            self.entrenamiento.finalizado_por,
            self.admin,
        )

    def test_perfil_inactivo_no_puede_finalizar(self):
        self.client.force_login(self.inactivo)

        self.client.post(
            reverse(
                "finalizar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertFalse(
            self.entrenamiento.finalizado,
        )

    def test_turno_sin_responsable_no_finaliza(self):
        self.entrenamiento.responsable_usuario = None
        self.entrenamiento.save(
            update_fields=["responsable_usuario"],
        )

        self.client.force_login(self.entrenador)

        self.client.post(
            reverse(
                "finalizar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertFalse(
            self.entrenamiento.finalizado,
        )

    def test_turno_con_asistencia_pendiente_no_finaliza(self):
        asistencia = self.entrenamiento.asistencias.get()
        asistencia.estado = "pendiente"
        asistencia.save(
            update_fields=["estado"],
        )

        self.client.force_login(self.entrenador)

        self.client.post(
            reverse(
                "finalizar_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertFalse(
            self.entrenamiento.finalizado,
        )

    def test_entrenador_activo_puede_reabrir(self):
        self.entrenamiento.finalizado = True
        self.entrenamiento.finalizado_por = self.entrenador
        self.entrenamiento.save(
            update_fields=[
                "finalizado",
                "finalizado_por",
            ]
        )

        self.client.force_login(self.entrenador)

        response = self.client.post(
            reverse(
                "reabrir_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.entrenamiento.finalizado)
        self.assertIsNone(
            self.entrenamiento.finalizado_por,
        )
        self.assertIsNone(
            self.entrenamiento.finalizado_el,
        )

    def test_perfil_inactivo_no_puede_reabrir(self):
        self.entrenamiento.finalizado = True
        self.entrenamiento.finalizado_por = self.entrenador
        self.entrenamiento.save(
            update_fields=[
                "finalizado",
                "finalizado_por",
            ]
        )

        self.client.force_login(self.inactivo)

        self.client.post(
            reverse(
                "reabrir_turno",
                args=[self.entrenamiento.id],
            )
        )

        self.entrenamiento.refresh_from_db()

        self.assertTrue(
            self.entrenamiento.finalizado,
        )
