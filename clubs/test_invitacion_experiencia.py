from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from clubs.models import Club, InvitacionClub, PerfilUsuario


@override_settings(APP_BASE_URL="http://127.0.0.1:8000")
class InvitacionClubExperienciaTests(TestCase):
    def setUp(self):
        self.invitacion = InvitacionClub.objects.create(
            referencia="Club Demo",
        )
        self.url = reverse(
            "registro_club_invitacion",
            kwargs={
                "token": self.invitacion.token,
            },
        )

    def datos_validos(self):
        return {
            "nombre_club": "Club Demo",
            "color_primario": "#2563EB",
            "color_secundario": "#111827",
            "email_club": "club@example.com",
            "nombre_admin": "Admin",
            "apellido_admin": "Demo",
            "email_admin": "admin.demo@example.com",
            "username": "admin_demo",
            "password": "ClaveDemo2026!Segura",
            "password_confirmacion": "ClaveDemo2026!Segura",
        }

    def test_link_usado_muestra_pantalla_amigable(self):
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
        self.assertContains(
            response,
            "Este link ya no está disponible",
            status_code=410,
        )

    def test_token_inexistente_muestra_misma_pantalla(self):
        url = reverse(
            "registro_club_invitacion",
            kwargs={
                "token": "11111111-1111-1111-1111-111111111111",
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            410,
        )
        self.assertContains(
            response,
            "Este link ya no está disponible",
            status_code=410,
        )

    def test_admin_muestra_link_absoluto(self):
        superusuario = User.objects.create_superuser(
            username="admin_tecnico_test",
            password="ClaveAdmin2026!",
        )
        self.client.force_login(superusuario)

        response = self.client.get(
            reverse(
                "admin:clubs_invitacionclub_change",
                args=[self.invitacion.pk],
            )
        )

        link_esperado = (
            "http://127.0.0.1:8000"
            + self.url
        )

        self.assertContains(
            response,
            link_esperado,
        )
