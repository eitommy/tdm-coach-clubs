from getpass import getpass

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from clubs.models import Club, PerfilUsuario


class Command(BaseCommand):
    help = (
        "Crea un club comercial y su primer administrador "
        "en una única operación."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--nombre",
            help="Nombre del club.",
        )
        parser.add_argument(
            "--username",
            help="Usuario del primer administrador.",
        )
        parser.add_argument(
            "--password",
            help=(
                "Contraseña del administrador. "
                "Si se omite, se pide de forma interactiva."
            ),
        )
        parser.add_argument(
            "--nombre-admin",
            default="",
            help="Nombre del administrador.",
        )
        parser.add_argument(
            "--apellido-admin",
            default="",
            help="Apellido del administrador.",
        )
        parser.add_argument(
            "--email-admin",
            default="",
            help="Email del administrador.",
        )
        parser.add_argument(
            "--email-club",
            default="",
            help="Email general del club.",
        )
        parser.add_argument(
            "--telefono",
            default="",
            help="Teléfono del club.",
        )
        parser.add_argument(
            "--direccion",
            default="",
            help="Dirección del club.",
        )

    def handle(self, *args, **options):
        nombre_club = (
            options.get("nombre")
            or input("Nombre del club: ")
        ).strip()

        username = (
            options.get("username")
            or input("Usuario del administrador: ")
        ).strip()

        if not nombre_club:
            raise CommandError(
                "El nombre del club es obligatorio."
            )

        if not username:
            raise CommandError(
                "El username del administrador es obligatorio."
            )

        if Club.objects.filter(
            nombre__iexact=nombre_club,
        ).exists():
            raise CommandError(
                "Ya existe un club con ese nombre."
            )

        if User.objects.filter(
            username__iexact=username,
        ).exists():
            raise CommandError(
                "Ya existe un usuario con ese username."
            )

        password = options.get("password")

        if not password:
            password = getpass(
                "Contraseña del administrador: "
            )
            confirmacion = getpass(
                "Repetir contraseña: "
            )

            if password != confirmacion:
                raise CommandError(
                    "Las contraseñas no coinciden."
                )

        usuario_temporal = User(
            username=username,
            first_name=options.get("nombre_admin", "").strip(),
            last_name=options.get("apellido_admin", "").strip(),
            email=options.get("email_admin", "").strip(),
        )

        try:
            validate_password(
                password,
                user=usuario_temporal,
            )
        except ValidationError as error:
            raise CommandError(
                "Contraseña inválida: "
                + " ".join(error.messages)
            ) from error

        with transaction.atomic():
            club = Club.objects.create(
                nombre=nombre_club,
                email=options.get("email_club", "").strip(),
                telefono=options.get("telefono", "").strip(),
                direccion=options.get("direccion", "").strip(),
                activo=True,
            )

            usuario = User.objects.create_user(
                username=username,
                password=password,
                first_name=options.get(
                    "nombre_admin",
                    "",
                ).strip(),
                last_name=options.get(
                    "apellido_admin",
                    "",
                ).strip(),
                email=options.get(
                    "email_admin",
                    "",
                ).strip(),
                is_active=True,
            )

            PerfilUsuario.objects.create(
                usuario=usuario,
                club=club,
                rol=PerfilUsuario.Rol.ADMIN,
                activo=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f'Club "{club.nombre}" creado correctamente. '
                    f'Administrador: "{usuario.username}".'
                )
            )
        )

        self.stdout.write(
            (
                "Estado de pago inicial: "
                f"{club.get_estado_pago_display()}."
            )
        )
