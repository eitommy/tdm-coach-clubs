from django.core.management.base import BaseCommand

from asistencia.models import Entrenamiento


class Command(BaseCommand):
    help = (
        "Audita si los entrenamientos comerciales todavía conservan "
        "un valor en el campo numérico legacy `turno`."
    )

    def handle(self, *args, **options):
        comerciales = (
            Entrenamiento.objects
            .filter(club__isnull=False)
            .select_related("club", "turno_config")
            .order_by("club__nombre", "fecha", "turno_config__orden")
        )

        total = comerciales.count()
        con_turno_legacy = comerciales.exclude(
            turno__isnull=True
        )
        sin_turno_legacy = comerciales.filter(
            turno__isnull=True
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "AUDITORÍA DEL CAMPO NUMÉRICO LEGACY `turno`"
            )
        )
        self.stdout.write("")

        self.stdout.write(
            f"Entrenamientos comerciales: {total}"
        )
        self.stdout.write(
            "Con valor legacy en `turno`: "
            f"{con_turno_legacy.count()}"
        )
        self.stdout.write(
            "Con `turno=NULL`: "
            f"{sin_turno_legacy.count()}"
        )

        if con_turno_legacy.exists():
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Registros comerciales que todavía guardan "
                    "el valor numérico:"
                )
            )

            for entrenamiento in con_turno_legacy:
                turno_config = entrenamiento.turno_config

                nombre_config = (
                    turno_config.nombre
                    if turno_config
                    else "Sin turno_config"
                )

                self.stdout.write(
                    "  - "
                    f"ID {entrenamiento.id} | "
                    f"{entrenamiento.club.nombre} | "
                    f"{entrenamiento.fecha} | "
                    f"{nombre_config} | "
                    f"turno legacy={entrenamiento.turno}"
                )

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Esto no rompe la app porque TurnoClub ya manda. "
                    "Antes de eliminar el campo definitivamente, "
                    "podemos poner esos valores comerciales en NULL."
                )
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Todos los entrenamientos comerciales ya tienen "
                    "`turno=NULL`. La parte comercial no guarda "
                    "el turno numérico."
                )
            )
