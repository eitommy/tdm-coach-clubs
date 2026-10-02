from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario


class CambioPasswordPropiaSesionTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Sesion",
        )

        self.admin = User.objects.create_user(
            username="admin_sesion",
            password="PasswordVieja123!",
            first_name="Admin",
            last_name="Sesion",
            email="admin@sesion.test",
        )

        self.perfil = PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

    def test_admin_sigue_logueado_al_cambiar_su_propia_password(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse(
                "editar_usuario",
                kwargs={"perfil_id": self.perfil.id},
            ),
            {
                "nombre": "Admin",
                "apellido": "Sesion",
                "email": "admin@sesion.test",
                "rol": PerfilUsuario.Rol.ADMIN,
                "activo": "on",
                "nueva_password": "PasswordNueva456!",
                "nueva_password_confirmacion": "PasswordNueva456!",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        self.admin.refresh_from_db()

        self.assertTrue(
            self.admin.check_password("PasswordNueva456!")
        )

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.admin.id,
        )

        response = self.client.get(
            reverse("lista_usuarios")
        )

        self.assertEqual(response.status_code, 200)
