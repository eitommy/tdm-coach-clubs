from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, InvitacionClub, PerfilUsuario


class RegistroClubInvitacionTests(TestCase):
    def setUp(self):
        self.invitacion = InvitacionClub.objects.create(
            referencia="Spin TDM",
        )
        self.url = reverse(
            "registro_club_invitacion",
            kwargs={
                "token": self.invitacion.token,
            },
        )

    def datos_validos(self):
        return {
            "nombre_club": "Spin TDM",
            "color_primario": "#123456",
            "color_secundario": "#654321",
            "email_club": "club@example.com",
            "nombre_admin": "Rodrigo",
            "apellido_admin": "Delgadillo",
            "email_admin": "rodrigo@example.com",
            "username": "rodrigo_spin",
            "password": "ClaveSpin2026!Segura",
            "password_confirmacion": "ClaveSpin2026!Segura",
        }

    def test_get_invitacion_disponible_muestra_formulario(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear tu club")
        self.assertContains(response, "Spin TDM")

    def test_registro_crea_club_admin_y_consume_invitacion(self):
        response = self.client.post(
            self.url,
            self.datos_validos(),
        )

        club = Club.objects.get(
            nombre="Spin TDM",
        )

        usuario = User.objects.get(
            username="rodrigo_spin",
        )

        perfil = PerfilUsuario.objects.get(
            usuario=usuario,
        )

        self.invitacion.refresh_from_db()

        self.assertEqual(
            response.status_code,
            302,
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
            perfil.activo,
        )
        self.assertEqual(
            self.invitacion.club_creado,
            club,
        )
        self.assertIsNotNone(
            self.invitacion.usada_en,
        )

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            usuario.pk,
        )

    def test_invitacion_usada_no_puede_reutilizarse(self):
        self.client.post(
            self.url,
            self.datos_validos(),
        )

        self.client.logout()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
    response.status_code,
    410,
)

    def test_username_duplicado_no_consume_invitacion(self):
        User.objects.create_user(
            username="rodrigo_spin",
            password="OtraClave2026!",
        )

        response = self.client.post(
            self.url,
            self.datos_validos(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "Ya existe un usuario con ese nombre.",
        )

        self.invitacion.refresh_from_db()

        self.assertIsNone(
            self.invitacion.usada_en,
        )
        self.assertFalse(
            Club.objects.filter(
                nombre="Spin TDM",
            ).exists()
        )
