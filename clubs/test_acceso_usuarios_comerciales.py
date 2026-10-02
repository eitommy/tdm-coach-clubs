from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario
from clubs.utils import (
    obtener_club_usuario,
    usuario_es_admin_club,
    usuario_es_entrenador,
)


class AccesoUsuariosComercialesTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Accesos",
            activo=True,
        )

        self.admin = User.objects.create_user(
            username="admin_accesos",
            password="TestPass123!",
            is_active=True,
        )
        self.perfil_admin = PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_accesos",
            password="TestPass123!",
            is_active=True,
        )
        self.perfil_entrenador = PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.sin_perfil = User.objects.create_user(
            username="sin_perfil",
            password="TestPass123!",
            is_active=True,
        )

        self.superuser_tecnico = User.objects.create_superuser(
            username="super_tecnico",
            email="tecnico@example.com",
            password="TestPass123!",
        )

    def test_admin_activo_tiene_club_y_rol_admin(self):
        self.assertEqual(
            obtener_club_usuario(self.admin),
            self.club,
        )
        self.assertTrue(
            usuario_es_admin_club(self.admin)
        )
        self.assertFalse(
            usuario_es_entrenador(self.admin)
        )

    def test_entrenador_activo_tiene_club_y_rol_entrenador(self):
        self.assertEqual(
            obtener_club_usuario(self.entrenador),
            self.club,
        )
        self.assertTrue(
            usuario_es_entrenador(self.entrenador)
        )
        self.assertFalse(
            usuario_es_admin_club(self.entrenador)
        )

    def test_perfil_inactivo_no_obtiene_club(self):
        self.perfil_entrenador.activo = False
        self.perfil_entrenador.save(update_fields=["activo"])

        self.assertIsNone(
            obtener_club_usuario(self.entrenador)
        )
        self.assertFalse(
            usuario_es_entrenador(self.entrenador)
        )
        self.assertFalse(
            usuario_es_admin_club(self.entrenador)
        )

    def test_club_inactivo_bloquea_perfiles(self):
        self.club.activo = False
        self.club.save(update_fields=["activo"])

        self.assertIsNone(
            obtener_club_usuario(self.admin)
        )
        self.assertFalse(
            usuario_es_admin_club(self.admin)
        )

    def test_usuario_sin_perfil_no_obtiene_club(self):
        self.assertIsNone(
            obtener_club_usuario(self.sin_perfil)
        )
        self.assertFalse(
            usuario_es_admin_club(self.sin_perfil)
        )
        self.assertFalse(
            usuario_es_entrenador(self.sin_perfil)
        )

    def test_superuser_tecnico_sin_perfil_no_obtiene_club(self):
        self.assertIsNone(
            obtener_club_usuario(self.superuser_tecnico)
        )
        self.assertFalse(
            usuario_es_admin_club(self.superuser_tecnico)
        )

    def test_entrenador_no_puede_entrar_panel_admin_club(self):
        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse("lista_usuarios")
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_si_puede_entrar_panel_admin_club(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("lista_usuarios")
        )

        self.assertEqual(response.status_code, 200)

    def test_perfil_inactivo_no_puede_entrar_panel_admin(self):
        self.perfil_admin.activo = False
        self.perfil_admin.save(update_fields=["activo"])

        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("lista_usuarios")
        )

        self.assertEqual(response.status_code, 403)

    def test_usuario_sin_perfil_no_puede_entrar_panel_admin(self):
        self.client.force_login(self.sin_perfil)

        response = self.client.get(
            reverse("lista_usuarios")
        )

        self.assertEqual(response.status_code, 403)

    def test_superuser_tecnico_no_entra_panel_comercial(self):
        self.client.force_login(self.superuser_tecnico)

        response = self.client.get(
            reverse("lista_usuarios")
        )

        self.assertEqual(response.status_code, 403)

    def test_entrenador_activo_puede_entrar_inicio_operativo(self):
        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(response.status_code, 200)

    def test_perfil_inactivo_no_puede_entrar_inicio_operativo(self):
        self.perfil_entrenador.activo = False
        self.perfil_entrenador.save(update_fields=["activo"])

        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertRedirects(
            response,
            reverse("login"),
            fetch_redirect_response=False,
        )

    def test_usuario_sin_perfil_no_puede_entrar_inicio_operativo(self):
        self.client.force_login(self.sin_perfil)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertRedirects(
            response,
            reverse("login"),
            fetch_redirect_response=False,
        )

    def test_superuser_tecnico_no_entra_inicio_comercial(self):
        self.client.force_login(self.superuser_tecnico)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertRedirects(
            response,
            reverse("login"),
            fetch_redirect_response=False,
        )

    def test_usuario_django_inactivo_no_accede_a_vistas_protegidas(self):
        usuario = User.objects.create_user(
            username="django_inactivo",
            password="TestPass123!",
            is_active=False,
        )
        PerfilUsuario.objects.create(
            usuario=usuario,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.client.force_login(usuario)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("login"),
            response.url,
        )
