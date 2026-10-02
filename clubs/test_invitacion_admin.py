from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.admin import InvitacionClubAdmin
from clubs.models import InvitacionClub


class InvitacionClubAdminTests(TestCase):
    def setUp(self):
        self.superusuario = User.objects.create_superuser(
            username="admin_invitaciones",
            email="admin@example.com",
            password="ClaveAdmin2026!",
        )
        self.client.force_login(self.superusuario)

    def test_modelo_esta_registrado_en_admin(self):
        self.assertIn(InvitacionClub, admin.site._registry)
        self.assertIsInstance(
            admin.site._registry[InvitacionClub],
            InvitacionClubAdmin,
        )

    def test_admin_puede_crear_invitacion(self):
        response = self.client.post(
            reverse("admin:clubs_invitacionclub_add"),
            {"referencia": "Spin TDM"},
        )
        self.assertEqual(response.status_code, 302)

        invitacion = InvitacionClub.objects.get(
            referencia="Spin TDM",
        )
        self.assertIsNotNone(invitacion.token)
        self.assertIsNone(invitacion.usada_en)

    def test_detalle_muestra_link_de_registro(self):
        invitacion = InvitacionClub.objects.create(
            referencia="Spin TDM",
        )

        response = self.client.get(
            reverse(
                "admin:clubs_invitacionclub_change",
                args=[invitacion.pk],
            )
        )
        self.assertEqual(response.status_code, 200)

        url_registro = reverse(
            "registro_club_invitacion",
            kwargs={"token": invitacion.token},
        )
        self.assertContains(response, url_registro)
