from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from clubs.models import Club, PerfilUsuario


class CrearClubComercialCommandTests(TestCase):
    def test_crea_club_usuario_y_perfil_admin(self):
        salida = StringIO()

        call_command(
            "crear_club_comercial",
            nombre="Club Nuevo",
            username="admin_nuevo",
            password="ClaveSegura2026!",
            nombre_admin="Ana",
            apellido_admin="Pérez",
            email_admin="ana@example.com",
            email_club="club@example.com",
            telefono="123456",
            direccion="Calle 123",
            stdout=salida,
        )

        club = Club.objects.get(
            nombre="Club Nuevo"
        )
        usuario = User.objects.get(
            username="admin_nuevo"
        )
        perfil = PerfilUsuario.objects.get(
            usuario=usuario
        )

        self.assertEqual(
            perfil.club,
            club,
        )
        self.assertEqual(
            perfil.rol,
            PerfilUsuario.Rol.ADMIN,
        )
        self.assertTrue(
            perfil.activo
        )
        self.assertTrue(
            usuario.is_active
        )
        self.assertTrue(
            usuario.check_password(
                "ClaveSegura2026!"
            )
        )

        self.assertEqual(
            club.email,
            "club@example.com",
        )
        self.assertEqual(
            club.estado_pago,
            Club.EstadoPago.PENDIENTE,
        )

        self.assertIn(
            'Club "Club Nuevo" creado correctamente.',
            salida.getvalue(),
        )

    def test_no_permite_club_duplicado_sin_importar_mayusculas(self):
        Club.objects.create(
            nombre="Club Repetido"
        )

        with self.assertRaises(CommandError):
            call_command(
                "crear_club_comercial",
                nombre="club repetido",
                username="admin_otro",
                password="ClaveSegura2026!",
            )

        self.assertFalse(
            User.objects.filter(
                username="admin_otro"
            ).exists()
        )

    def test_no_permite_username_duplicado_sin_importar_mayusculas(self):
        User.objects.create_user(
            username="AdminExistente",
            password="ClaveSegura2026!",
        )

        with self.assertRaises(CommandError):
            call_command(
                "crear_club_comercial",
                nombre="Club Sin Crear",
                username="adminexistente",
                password="ClaveSegura2026!",
            )

        self.assertFalse(
            Club.objects.filter(
                nombre="Club Sin Crear"
            ).exists()
        )

    def test_rechaza_password_invalida_y_no_crea_datos(self):
        with self.assertRaises(CommandError):
            call_command(
                "crear_club_comercial",
                nombre="Club Fallido",
                username="admin_fallido",
                password="123",
            )

        self.assertFalse(
            Club.objects.filter(
                nombre="Club Fallido"
            ).exists()
        )
        self.assertFalse(
            User.objects.filter(
                username="admin_fallido"
            ).exists()
        )
