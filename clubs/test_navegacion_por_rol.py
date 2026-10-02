from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario


class NavegacionPorRolTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Navegación",
            activo=True,
        )

        self.admin = User.objects.create_user(
            username="admin_nav",
            password="TestPass123!",
            first_name="Admin",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_nav",
            password="TestPass123!",
            first_name="Entrenador",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

    def test_admin_ve_menu_administracion(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Administración",
        )

        self.assertContains(
            response,
            "Configuración del club",
        )

        self.assertContains(
            response,
            "Usuarios",
        )

        self.assertContains(
            response,
            reverse("configuracion_club"),
        )

        self.assertContains(
            response,
            reverse("lista_usuarios"),
        )

    def test_entrenador_no_ve_menu_administracion(self):
        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            "Administración",
        )

        self.assertNotContains(
            response,
            "Configuración del club",
        )

        self.assertNotContains(
            response,
            reverse("configuracion_club"),
        )

        self.assertNotContains(
            response,
            reverse("lista_usuarios"),
        )

    def test_entrenador_ve_navegacion_operativa(self):
        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        textos = [
            "Carga diaria",
            "Jugadores",
            "Reportes",
            "Resumen del día",
            "Base de ejercicios",
            "Turnos",
            "Seguimiento semanal",
            "Resumen mensual",
            "Ayuda",
        ]

        for texto in textos:
            with self.subTest(texto=texto):
                self.assertContains(
                    response,
                    texto,
                )

        self.assertContains(
            response,
            reverse("lista_turnos"),
        )

    def test_admin_ve_navegacion_operativa(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        textos = [
            "Carga diaria",
            "Jugadores",
            "Reportes",
            "Resumen del día",
            "Base de ejercicios",
            "Turnos",
            "Seguimiento semanal",
            "Resumen mensual",
            "Ayuda",
        ]

        for texto in textos:
            with self.subTest(texto=texto):
                self.assertContains(
                    response,
                    texto,
                )

    def test_badge_muestra_rol_correcto(self):
        self.client.force_login(self.admin)

        response_admin = self.client.get(
            reverse("inicio")
        )

        self.assertContains(
            response_admin,
            "Administrador",
        )

        self.client.force_login(
            self.entrenador
        )

        response_entrenador = self.client.get(
            reverse("inicio")
        )

        self.assertContains(
            response_entrenador,
            "Entrenador",
        )

    def test_menu_usuario_muestra_perfil_y_cambio_password(self):
        for usuario in [
            self.admin,
            self.entrenador,
        ]:
            with self.subTest(
                usuario=usuario.username
            ):
                self.client.force_login(
                    usuario
                )

                response = self.client.get(
                    reverse("inicio")
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

                self.assertContains(
                    response,
                    "Mi perfil",
                )

                self.assertContains(
                    response,
                    "Cambiar contraseña",
                )

                self.assertContains(
                    response,
                    reverse("mi_perfil"),
                )

                self.assertContains(
                    response,
                    reverse("password_change"),
                )