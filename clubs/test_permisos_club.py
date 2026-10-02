from datetime import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub


class PermisosAdministracionClubTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club A",
        )

        self.otro_club = Club.objects.create(
            nombre="Club B",
        )

        self.admin = User.objects.create_user(
            username="admin_a",
            password="TestPass123!",
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_a",
            password="TestPass123!",
        )

        self.admin_otro = User.objects.create_user(
            username="admin_b",
            password="TestPass123!",
        )

        self.perfil_admin = PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.perfil_entrenador = PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.perfil_admin_otro = PerfilUsuario.objects.create(
            usuario=self.admin_otro,
            club=self.otro_club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.turno_otro = TurnoClub.objects.create(
            club=self.otro_club,
            dia_semana=0,
            nombre="Turno externo",
            hora_inicio=time(18, 0),
            hora_fin=time(20, 0),
            orden=1,
            activo=True,
        )

    def test_entrenador_no_puede_entrar_a_configuracion(self):
        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse("configuracion_club")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_entrenador_puede_gestionar_turnos(self):
        self.client.force_login(self.entrenador)

        for nombre_url in [
            "lista_turnos",
            "crear_turno",
        ]:
            with self.subTest(url=nombre_url):
                response = self.client.get(
                    reverse(nombre_url)
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

    def test_entrenador_no_puede_gestionar_usuarios(self):
        self.client.force_login(self.entrenador)

        for nombre_url in [
            "lista_usuarios",
            "crear_usuario",
        ]:
            with self.subTest(url=nombre_url):
                response = self.client.get(
                    reverse(nombre_url)
                )

                self.assertEqual(
                    response.status_code,
                    403,
                )

    def test_admin_puede_entrar_a_administracion(self):
        self.client.force_login(self.admin)

        for nombre_url in [
            "configuracion_club",
            "lista_turnos",
            "crear_turno",
            "lista_usuarios",
            "crear_usuario",
        ]:
            with self.subTest(url=nombre_url):
                response = self.client.get(
                    reverse(nombre_url)
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

    def test_admin_no_puede_editar_usuario_de_otro_club(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "editar_usuario",
                args=[self.perfil_admin_otro.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_admin_no_puede_editar_turno_de_otro_club(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "editar_turno",
                args=[self.turno_otro.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_entrenador_no_puede_editar_turno_de_otro_club(self):
        self.client.force_login(self.entrenador)

        response = self.client.get(
            reverse(
                "editar_turno",
                args=[self.turno_otro.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
