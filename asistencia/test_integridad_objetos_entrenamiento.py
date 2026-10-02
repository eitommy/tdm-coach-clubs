from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from clubs.models import Club, TurnoClub
from asistencia.models import (
    Asistencia,
    CategoriaEjercicio,
    Ejercicio,
    EjercicioTurno,
    Entrenamiento,
    Jugador,
    ObservacionJugador,
    PartidoTurno,
    TrabajoTurno,
)


class IntegridadObjetosEntrenamientoMulticlubTests(TestCase):
    def setUp(self):
        self.club_a = Club.objects.create(nombre="Club A")
        self.club_b = Club.objects.create(nombre="Club B")

        self.turno_a = TurnoClub.objects.create(
            club=self.club_a,
            dia_semana=0,
            nombre="Turno A",
            hora_inicio=time(15, 0),
            hora_fin=time(17, 0),
            orden=1,
            activo=True,
        )

        self.entrenamiento_a = Entrenamiento.objects.create(
            club=self.club_a,
            fecha=timezone.localdate(),
            turno_config=self.turno_a,
        )

        self.jugador_a1 = Jugador.objects.create(
            club=self.club_a,
            nombre="Jugador",
            apellido="A1",
            activo=True,
        )
        self.jugador_a2 = Jugador.objects.create(
            club=self.club_a,
            nombre="Jugador",
            apellido="A2",
            activo=True,
        )
        self.jugador_b = Jugador.objects.create(
            club=self.club_b,
            nombre="Jugador",
            apellido="B",
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

        self.ejercicio_a = Ejercicio.objects.create(
            club=self.club_a,
            nombre="Ejercicio A",
            categoria_config=self.categoria_a,
            activo=True,
        )
        self.ejercicio_b = Ejercicio.objects.create(
            club=self.club_b,
            nombre="Ejercicio B",
            categoria_config=self.categoria_b,
            activo=True,
        )

    def test_asistencia_rechaza_jugador_de_otro_club(self):
        objeto = Asistencia(
            entrenamiento=self.entrenamiento_a,
            jugador=self.jugador_b,
            estado="asistio",
        )

        with self.assertRaises(ValidationError) as error:
            objeto.full_clean()

        self.assertIn("jugador", error.exception.message_dict)

    def test_trabajo_rechaza_jugador_de_otro_club(self):
        objeto = TrabajoTurno(
            entrenamiento=self.entrenamiento_a,
            cambio=1,
            tipo=TrabajoTurno.Tipo.LIBRE,
            jugador_1=self.jugador_b,
        )

        with self.assertRaises(ValidationError) as error:
            objeto.full_clean()

        self.assertIn("jugador_1", error.exception.message_dict)

    def test_ejercicio_turno_rechaza_ejercicio_de_otro_club(self):
        objeto = EjercicioTurno(
            entrenamiento=self.entrenamiento_a,
            ejercicio=self.ejercicio_b,
        )

        with self.assertRaises(ValidationError) as error:
            objeto.full_clean()

        self.assertIn("ejercicio", error.exception.message_dict)

    def test_observacion_rechaza_jugador_de_otro_club(self):
        objeto = ObservacionJugador(
            entrenamiento=self.entrenamiento_a,
            jugador=self.jugador_b,
            texto="Observación",
        )

        with self.assertRaises(ValidationError) as error:
            objeto.full_clean()

        self.assertIn("jugador", error.exception.message_dict)

    def test_partido_rechaza_jugador_de_otro_club(self):
        objeto = PartidoTurno(
            entrenamiento=self.entrenamiento_a,
            jugador_1=self.jugador_a1,
            jugador_2=self.jugador_b,
        )

        with self.assertRaises(ValidationError) as error:
            objeto.full_clean()

        self.assertIn("jugador_2", error.exception.message_dict)

    def test_relaciones_del_mismo_club_son_validas(self):
        Asistencia(
            entrenamiento=self.entrenamiento_a,
            jugador=self.jugador_a1,
            estado="asistio",
        ).full_clean()

        TrabajoTurno(
            entrenamiento=self.entrenamiento_a,
            cambio=1,
            tipo=TrabajoTurno.Tipo.PAREJA,
            jugador_1=self.jugador_a1,
            jugador_2=self.jugador_a2,
        ).full_clean()

        EjercicioTurno(
            entrenamiento=self.entrenamiento_a,
            ejercicio=self.ejercicio_a,
        ).full_clean()

        ObservacionJugador(
            entrenamiento=self.entrenamiento_a,
            jugador=self.jugador_a1,
            texto="Observación válida",
        ).full_clean()

        PartidoTurno(
            entrenamiento=self.entrenamiento_a,
            jugador_1=self.jugador_a1,
            jugador_2=self.jugador_a2,
        ).full_clean()
