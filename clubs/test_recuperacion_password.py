from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from clubs.models import Club, PerfilUsuario


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class RecuperacionPasswordTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Password",
            activo=True,
        )

        self.usuario = User.objects.create_user(
            username="entrenador_password",
            password="ClaveAnterior2026!",
            email="entrenador@example.com",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

    def test_login_muestra_link_olvide_password(self):
        response = self.client.get(
            reverse("login")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "¿Olvidaste tu contraseña?",
        )

        self.assertContains(
            response,
            reverse("password_reset"),
        )

    def test_email_registrado_recibe_enlace_reset(self):
        response = self.client.post(
            reverse("password_reset"),
            {
                "email": "entrenador@example.com",
            },
        )

        self.assertRedirects(
            response,
            reverse("password_reset_done"),
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertIn(
            "/accounts/reset/",
            mail.outbox[0].body,
        )

    def test_email_desconocido_no_revela_si_existe(self):
        response = self.client.post(
            reverse("password_reset"),
            {
                "email": "nadie@example.com",
            },
        )

        self.assertRedirects(
            response,
            reverse("password_reset_done"),
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_usuario_inactivo_no_recibe_reset(self):
        self.usuario.is_active = False

        self.usuario.save(
            update_fields=["is_active"],
        )

        response = self.client.post(
            reverse("password_reset"),
            {
                "email": "entrenador@example.com",
            },
        )

        self.assertRedirects(
            response,
            reverse("password_reset_done"),
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )
