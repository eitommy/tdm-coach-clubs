from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from asistencia.models import Entrenamiento


class Command(BaseCommand):
    help = (
        "Audita entrenamientos legacy y muestra cuáles todavía "
        "no tienen club o turno_config."
    )

    def handle(self, *args, **options):
        qs = Entrenamiento.objects.all()

        total = qs.count()
        con_club = qs.filter(club__isnull=False).count()
        sin_club = qs.filter(club__isnull=True).count()

        con_turno_config = qs.filter(
            turno_config__isnull=False
        ).count()

        sin_turno_config = qs.filter(
            turno_config__isnull=True
        ).count()

        comerciales_incompletos = qs.filter(
            club__isnull=False,
            turno_config__isnull=True,
        )

        legacy_puros = qs.filter(
            club__isnull=True,
            turno_config__isnull=True,
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "AUDITORÍA DE TURNOS LEGACY"
            )
        )
        self.stdout.write("")

        self.stdout.write(f"Total entrenamientos: {total}")
        self.stdout.write(f"Con club: {con_club}")
        self.stdout.write(f"Sin club: {sin_club}")
        self.stdout.write(
            f"Con turno_config: {con_turno_config}"
        )
        self.stdout.write(
            f"Sin turno_config: {sin_turno_config}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "Con club pero SIN turno_config: "
                f"{comerciales_incompletos.count()}"
            )
        )

        for entrenamiento in (
            comerciales_incompletos
            .select_related("club")
            .order_by("club__nombre", "fecha", "turno")
        ):
            self.stdout.write(
                "  - "
                f"ID {entrenamiento.id} | "
                f"{entrenamiento.club.nombre} | "
                f"{entrenamiento.fecha} | "
                f"turno legacy={entrenamiento.turno}"
            )

        self.stdout.write("")
        self.stdout.write(
            "Legacy sin club y sin turno_config: "
            f"{legacy_puros.count()}"
        )

        if comerciales_incompletos.exists():
            self.stdout.write("")
            self.stdout.write(
                self.style.ERROR(
                    "TODAVÍA NO conviene eliminar el campo legacy "
                    "`turno`: hay registros comerciales incompletos."
                )
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "No hay registros comerciales con turno_config "
                    "faltante. El siguiente paso puede ser auditar "
                    "dependencias de código antes de eliminar `turno`."
                )
            )

        self.stdout.write("")
        self.stdout.write("Resumen por club:")

        resumen = (
            qs.filter(club__isnull=False)
            .values("club__nombre")
            .annotate(
                total=Count("id"),
                sin_turno_config=Count(
                    "id",
                    filter=Q(turno_config__isnull=True),
                ),
            )
            .order_by("club__nombre")
        )

        for fila in resumen:
            self.stdout.write(
                "  - "
                f"{fila['club__nombre']}: "
                f"{fila['total']} total, "
                f"{fila['sin_turno_config']} sin turno_config"
            )
