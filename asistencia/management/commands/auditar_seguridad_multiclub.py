from django.core.management.base import BaseCommand
from django.db.models import F, Q

from asistencia.models import (
    Asistencia,
    EjercicioTurno,
    ObservacionJugador,
    PartidoTurno,
    TrabajoTurno,
)


class Command(BaseCommand):
    help = (
        "Audita relaciones comerciales para detectar objetos que mezclen "
        "datos entre clubes distintos."
    )

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "AUDITORÍA DE SEGURIDAD MULTICLUB"
            )
        )
        self.stdout.write("")

        problemas = []

        asistencias = Asistencia.objects.filter(
            entrenamiento__club__isnull=False,
        ).exclude(
            jugador__club=F("entrenamiento__club"),
        )
        problemas.append(
            (
                "Asistencias con jugador de otro club",
                asistencias.count(),
            )
        )

        observaciones = ObservacionJugador.objects.filter(
            entrenamiento__club__isnull=False,
        ).exclude(
            jugador__club=F("entrenamiento__club"),
        )
        problemas.append(
            (
                "Observaciones con jugador de otro club",
                observaciones.count(),
            )
        )

        ejercicios_turno = EjercicioTurno.objects.filter(
            entrenamiento__club__isnull=False,
        ).exclude(
            ejercicio__club=F("entrenamiento__club"),
        )
        problemas.append(
            (
                "Ejercicios de turno pertenecientes a otro club",
                ejercicios_turno.count(),
            )
        )

        trabajos = TrabajoTurno.objects.filter(
            entrenamiento__club__isnull=False,
        ).filter(
            Q(jugador_1__isnull=False)
            & ~Q(jugador_1__club=F("entrenamiento__club"))
            |
            Q(jugador_2__isnull=False)
            & ~Q(jugador_2__club=F("entrenamiento__club"))
        )
        problemas.append(
            (
                "Trabajos con jugadores de otro club",
                trabajos.distinct().count(),
            )
        )

        partidos = PartidoTurno.objects.filter(
            entrenamiento__club__isnull=False,
        ).filter(
            ~Q(jugador_1__club=F("entrenamiento__club"))
            | ~Q(jugador_2__club=F("entrenamiento__club"))
        )
        problemas.append(
            (
                "Partidos con jugadores de otro club",
                partidos.distinct().count(),
            )
        )

        total_problemas = 0

        for nombre, cantidad in problemas:
            total_problemas += cantidad

            if cantidad:
                self.stdout.write(
                    self.style.ERROR(
                        f"{nombre}: {cantidad}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{nombre}: 0"
                    )
                )

        self.stdout.write("")

        if total_problemas:
            self.stdout.write(
                self.style.ERROR(
                    f"Se detectaron {total_problemas} relaciones "
                    "potencialmente cruzadas entre clubes."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "No se detectaron relaciones cruzadas entre clubes."
                )
            )
