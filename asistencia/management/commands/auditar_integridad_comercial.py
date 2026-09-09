from django.core.management.base import BaseCommand
from django.db.models import F, Q

from clubs.models import PerfilUsuario
from asistencia.models import (
    Asistencia,
    EjercicioTurno,
    Entrenamiento,
    ObservacionJugador,
    PartidoTurno,
    TrabajoTurno,
)


class Command(BaseCommand):
    help = (
        "Ejecuta controles básicos de integridad de la parte comercial "
        "multiclub sin modificar datos."
    )

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "CHEQUEO DE INTEGRIDAD COMERCIAL"
            )
        )
        self.stdout.write("")

        errores = []

        comerciales = Entrenamiento.objects.filter(
            club__isnull=False,
        )

        checks = [
            (
                "Entrenamientos comerciales sin turno_config",
                comerciales.filter(
                    turno_config__isnull=True,
                ).count(),
            ),
            (
                "Entrenamientos comerciales con turno legacy",
                comerciales.exclude(
                    turno__isnull=True,
                ).count(),
            ),
            (
                "Entrenamientos comerciales con entrenador legacy",
                comerciales.filter(
                    Q(entrenador__isnull=False)
                    | Q(entrenador_responsable__isnull=False)
                ).count(),
            ),
            (
                "Asistencias con jugador de otro club",
                Asistencia.objects.filter(
                    entrenamiento__club__isnull=False,
                ).exclude(
                    jugador__club=F("entrenamiento__club"),
                ).count(),
            ),
            (
                "Observaciones con jugador de otro club",
                ObservacionJugador.objects.filter(
                    entrenamiento__club__isnull=False,
                ).exclude(
                    jugador__club=F("entrenamiento__club"),
                ).count(),
            ),
            (
                "Ejercicios de turno de otro club",
                EjercicioTurno.objects.filter(
                    entrenamiento__club__isnull=False,
                ).exclude(
                    ejercicio__club=F("entrenamiento__club"),
                ).count(),
            ),
            (
                "Trabajos con jugadores de otro club",
                TrabajoTurno.objects.filter(
                    entrenamiento__club__isnull=False,
                ).filter(
                    (
                        Q(jugador_1__isnull=False)
                        & ~Q(
                            jugador_1__club=F(
                                "entrenamiento__club"
                            )
                        )
                    )
                    |
                    (
                        Q(jugador_2__isnull=False)
                        & ~Q(
                            jugador_2__club=F(
                                "entrenamiento__club"
                            )
                        )
                    )
                ).distinct().count(),
            ),
            (
                "Partidos con jugadores de otro club",
                PartidoTurno.objects.filter(
                    entrenamiento__club__isnull=False,
                ).filter(
                    ~Q(
                        jugador_1__club=F(
                            "entrenamiento__club"
                        )
                    )
                    |
                    ~Q(
                        jugador_2__club=F(
                            "entrenamiento__club"
                        )
                    )
                ).distinct().count(),
            ),
        ]

        perfiles_inconsistentes = 0

        for perfil in PerfilUsuario.objects.select_related(
            "usuario"
        ):
            if perfil.activo != perfil.usuario.is_active:
                perfiles_inconsistentes += 1

        checks.append(
            (
                "Usuarios con estado activo desincronizado",
                perfiles_inconsistentes,
            )
        )

        for nombre, cantidad in checks:
            if cantidad:
                errores.append((nombre, cantidad))
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
        self.stdout.write(
            f"Entrenamientos comerciales auditados: "
            f"{comerciales.count()}"
        )
        self.stdout.write(
            f"Perfiles comerciales auditados: "
            f"{PerfilUsuario.objects.count()}"
        )
        self.stdout.write("")

        if errores:
            self.stdout.write(
                self.style.ERROR(
                    "El chequeo encontró problemas de integridad."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Integridad comercial OK."
                )
            )
