from django.core.management.base import BaseCommand

from clubs.models import PerfilUsuario


class Command(BaseCommand):
    help = (
        "Audita que PerfilUsuario.activo y User.is_active estén "
        "sincronizados en los usuarios comerciales."
    )

    def handle(self, *args, **options):
        perfiles = (
            PerfilUsuario.objects
            .select_related("usuario", "club")
            .order_by("club__nombre", "usuario__username")
        )

        inconsistentes = []

        for perfil in perfiles:
            if perfil.activo != perfil.usuario.is_active:
                inconsistentes.append(perfil)

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "AUDITORÍA DE ESTADO DE USUARIOS"
            )
        )
        self.stdout.write("")

        self.stdout.write(
            f"Perfiles comerciales: {perfiles.count()}"
        )
        self.stdout.write(
            f"Estados inconsistentes: {len(inconsistentes)}"
        )

        if inconsistentes:
            self.stdout.write("")

            for perfil in inconsistentes:
                self.stdout.write(
                    self.style.WARNING(
                        "  - "
                        f"{perfil.club.nombre} | "
                        f"{perfil.usuario.username} | "
                        f"perfil.activo={perfil.activo} | "
                        f"user.is_active={perfil.usuario.is_active}"
                    )
                )

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Hay usuarios cuyo estado de acceso no coincide. "
                    "No se modificó ningún registro."
                )
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Todos los usuarios comerciales tienen el estado "
                    "de acceso sincronizado."
                )
            )
