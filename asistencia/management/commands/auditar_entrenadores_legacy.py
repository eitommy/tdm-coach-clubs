from django.core.management.base import BaseCommand

from asistencia.models import Entrenamiento


class Command(BaseCommand):
    help = (
        "Audita campos legacy de entrenador en entrenamientos comerciales."
    )

    def handle(self, *args, **options):
        comerciales = (
            Entrenamiento.objects
            .filter(club__isnull=False)
            .select_related(
                "club",
                "responsable_usuario",
                "entrenador_responsable",
                "entrenador",
            )
            .order_by("club__nombre", "fecha")
        )

        con_entrenador = comerciales.exclude(entrenador__isnull=True)
        con_entrenador_responsable = comerciales.exclude(
            entrenador_responsable__isnull=True
        )
        con_responsable_usuario = comerciales.exclude(
            responsable_usuario__isnull=True
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "AUDITORÍA DE ENTRENADORES LEGACY"
            )
        )
        self.stdout.write("")

        self.stdout.write(
            f"Entrenamientos comerciales: {comerciales.count()}"
        )
        self.stdout.write(
            "Con responsable_usuario: "
            f"{con_responsable_usuario.count()}"
        )
        self.stdout.write(
            "Con entrenador legacy (User): "
            f"{con_entrenador.count()}"
        )
        self.stdout.write(
            "Con entrenador_responsable legacy: "
            f"{con_entrenador_responsable.count()}"
        )

        legacy = comerciales.filter(
            entrenador__isnull=False
        ) | comerciales.filter(
            entrenador_responsable__isnull=False
        )

        if legacy.exists():
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Registros comerciales con datos legacy:"
                )
            )

            for entrenamiento in legacy.distinct():
                self.stdout.write(
                    "  - "
                    f"ID {entrenamiento.id} | "
                    f"{entrenamiento.club.nombre} | "
                    f"{entrenamiento.fecha} | "
                    f"responsable_usuario="
                    f"{entrenamiento.responsable_usuario or '-'} | "
                    f"entrenador="
                    f"{entrenamiento.entrenador or '-'} | "
                    f"entrenador_responsable="
                    f"{entrenamiento.entrenador_responsable or '-'}"
                )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "La parte comercial ya no guarda campos legacy "
                    "de entrenador."
                )
            )
