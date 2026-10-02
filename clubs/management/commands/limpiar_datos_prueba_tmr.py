from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from asistencia.models import CategoriaEjercicio, Ejercicio, Entrenamiento, Jugador
from clubs.models import Club, TurnoClub


class Command(BaseCommand):
    help = "Limpia datos operativos de prueba de TMR sin borrar club ni usuarios."

    def add_arguments(self, parser):
        parser.add_argument("--confirmar", action="store_true")

    def handle(self, *args, **options):
        if not options["confirmar"]:
            raise CommandError(
                "Operación cancelada. Ejecutá nuevamente con --confirmar."
            )

        try:
            club = Club.objects.get(nombre__iexact="TMR")
        except Club.DoesNotExist as exc:
            raise CommandError('No se encontró un club llamado "TMR".') from exc
        except Club.MultipleObjectsReturned as exc:
            raise CommandError(
                'Hay más de un club llamado "TMR". Revisá la base.'
            ) from exc

        resumen = {
            "entrenamientos": Entrenamiento.objects.filter(club=club).count(),
            "ejercicios": Ejercicio.objects.filter(club=club).count(),
            "categorias": CategoriaEjercicio.objects.filter(club=club).count(),
            "jugadores": Jugador.objects.filter(club=club).count(),
            "turnos": TurnoClub.objects.filter(club=club).count(),
        }

        with transaction.atomic():
            Entrenamiento.objects.filter(club=club).delete()
            Ejercicio.objects.filter(club=club).delete()
            CategoriaEjercicio.objects.filter(club=club).delete()
            Jugador.objects.filter(club=club).delete()
            TurnoClub.objects.filter(club=club).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Datos operativos de "{club.nombre}" eliminados.'
        ))
        self.stdout.write("El club y sus usuarios NO fueron eliminados.")
        for nombre, cantidad in resumen.items():
            self.stdout.write(f"- {nombre}: {cantidad}")
