from datetime import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clubs.models import Club, PerfilUsuario, TurnoClub
from asistencia.models import (
    Asistencia,
    Entrenamiento,
    Jugador,
    ObservacionJugador,
    PartidoTurno,
    TrabajoTurno,
)


class SeguridadMulticlubAccionesEntrenamientoTests(TestCase):
    def setUp(self):
        self.club_a = Club.objects.create(nombre="Club A")
        self.club_b = Club.objects.create(nombre="Club B")

        self.admin_a = User.objects.create_user(
            username="admin_a_acciones",
            password="TestPass123!",
        )
        self.admin_b = User.objects.create_user(
            username="admin_b_acciones",
            password="TestPass123!",
        )

        PerfilUsuario.objects.create(
            usuario=self.admin_a,
            club=self.club_a,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )
        PerfilUsuario.objects.create(
            usuario=self.admin_b,
            club=self.club_b,
            rol=PerfilUsuario.Rol.ADMIN,
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
            hora_inicio=time(18, 0),
            hora_fin=time(20, 0),
            orden=1,
            activo=True,
        )

        fecha = timezone.localdate()

        self.entrenamiento_a = Entrenamiento.objects.create(
            club=self.club_a,
            fecha=fecha,
            turno_config=self.turno_a,
        )
        self.entrenamiento_b = Entrenamiento.objects.create(
            club=self.club_b,
            fecha=fecha,
            turno_config=self.turno_b,
        )

        self.jugador_a = Jugador.objects.create(
            club=self.club_a,
            nombre="Jugador",
            apellido="A",
            activo=True,
        )
        self.jugador_b1 = Jugador.objects.create(
            club=self.club_b,
            nombre="Jugador",
            apellido="B1",
            activo=True,
        )
        self.jugador_b2 = Jugador.objects.create(
            club=self.club_b,
            nombre="Jugador",
            apellido="B2",
            activo=True,
        )

        self.asistencia_b = Asistencia.objects.create(
            entrenamiento=self.entrenamiento_b,
            jugador=self.jugador_b1,
            estado="asistio",
        )

        self.trabajo_b = TrabajoTurno.objects.create(
            entrenamiento=self.entrenamiento_b,
            cambio=1,
            tipo=TrabajoTurno.Tipo.LIBRE,
            jugador_1=self.jugador_b1,
            detalle="Trabajo club B",
        )

        self.observacion_b = ObservacionJugador.objects.create(
            jugador=self.jugador_b1,
            entrenamiento=self.entrenamiento_b,
            texto="Observación privada del Club B",
            creada_por=self.admin_b,
        )

        self.partido_b = PartidoTurno.objects.create(
            entrenamiento=self.entrenamiento_b,
            jugador_1=self.jugador_b1,
            jugador_2=self.jugador_b2,
            detalle="Partido Club B",
        )

        self.client.force_login(self.admin_a)

    def test_no_puede_editar_trabajo_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_trabajo_turno",
                kwargs={"trabajo_id": self.trabajo_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_no_puede_eliminar_trabajo_de_otro_club(self):
        response = self.client.post(
            reverse(
                "eliminar_trabajo_turno",
                kwargs={"trabajo_id": self.trabajo_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            TrabajoTurno.objects.filter(pk=self.trabajo_b.pk).exists()
        )

    def test_no_puede_editar_observacion_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_observacion_jugador",
                kwargs={"observacion_id": self.observacion_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_no_puede_eliminar_observacion_de_otro_club(self):
        response = self.client.post(
            reverse(
                "eliminar_observacion_jugador",
                kwargs={"observacion_id": self.observacion_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            ObservacionJugador.objects.filter(
                pk=self.observacion_b.pk
            ).exists()
        )

    def test_no_puede_editar_partido_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_partido_turno",
                kwargs={"partido_id": self.partido_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_no_puede_eliminar_partido_de_otro_club(self):
        response = self.client.post(
            reverse(
                "eliminar_partido_turno",
                kwargs={"partido_id": self.partido_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            PartidoTurno.objects.filter(pk=self.partido_b.pk).exists()
        )

    def test_no_puede_cambiar_asistencia_de_otro_club(self):
        estado_antes = self.asistencia_b.estado

        response = self.client.post(
            reverse(
                "cambiar_estado",
                kwargs={"asistencia_id": self.asistencia_b.id},
            ),
            {"estado": "ausente"},
        )

        self.assertEqual(response.status_code, 404)

        self.asistencia_b.refresh_from_db()
        self.assertEqual(self.asistencia_b.estado, estado_antes)

    def test_no_puede_quitar_jugador_de_otro_club(self):
        response = self.client.post(
            reverse(
                "quitar_jugador",
                kwargs={"asistencia_id": self.asistencia_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Asistencia.objects.filter(pk=self.asistencia_b.pk).exists()
        )

    def test_no_puede_agregar_trabajo_a_entrenamiento_de_otro_club(self):
        response = self.client.post(
            reverse(
                "agregar_trabajo_turno",
                kwargs={"entrenamiento_id": self.entrenamiento_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_no_puede_crear_partido_en_entrenamiento_de_otro_club(self):
        response = self.client.get(
            reverse(
                "crear_partido_turno",
                kwargs={"entrenamiento_id": self.entrenamiento_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_no_puede_finalizar_entrenamiento_de_otro_club(self):
        response = self.client.post(
            reverse(
                "finalizar_turno",
                kwargs={"entrenamiento_id": self.entrenamiento_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

        self.entrenamiento_b.refresh_from_db()
        self.assertFalse(self.entrenamiento_b.finalizado)

    def test_no_puede_reabrir_entrenamiento_de_otro_club(self):
        self.entrenamiento_b.finalizado = True
        self.entrenamiento_b.save(update_fields=["finalizado"])

        response = self.client.post(
            reverse(
                "reabrir_turno",
                kwargs={"entrenamiento_id": self.entrenamiento_b.id},
            )
        )
        self.assertEqual(response.status_code, 404)

        self.entrenamiento_b.refresh_from_db()
        self.assertTrue(self.entrenamiento_b.finalizado)
