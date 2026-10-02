from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from asistencia.models import Entrenamiento
from clubs.models import Club


CLUB_NOMBRE = "QA Carga Diaria"
USUARIOS_QA = [
    "qa_carga_admin",
    "qa_carga_entrenador",
]


class Command(BaseCommand):
    help = "Elimina el club temporal usado para probar carga diaria."

    @transaction.atomic
    def handle(self, *args, **options):
        club = Club.objects.filter(nombre=CLUB_NOMBRE).first()

        if club:
            Entrenamiento.objects.filter(club=club).delete()
            club.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Club temporal "{CLUB_NOMBRE}" eliminado.'
                )
            )
        else:
            self.stdout.write(
                'No existía el club temporal "QA Carga Diaria".'
            )

        eliminados, _ = User.objects.filter(
            username__in=USUARIOS_QA,
        ).delete()

        if eliminados:
            self.stdout.write(
                self.style.SUCCESS("Usuarios QA eliminados.")
            )
