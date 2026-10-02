from datetime import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub


class SeguridadMulticlubAdminClubTests(TestCase):
    def setUp(self):
        self.club_a = Club.objects.create(nombre="Club A")
        self.club_b = Club.objects.create(nombre="Club B")

        self.admin_a = User.objects.create_user(
            username="admin_a_panel",
            password="TestPass123!",
            first_name="Admin",
            last_name="A",
        )
        self.admin_b = User.objects.create_user(
            username="admin_b_panel",
            password="TestPass123!",
            first_name="Admin",
            last_name="B",
        )

        self.perfil_a = PerfilUsuario.objects.create(
            usuario=self.admin_a,
            club=self.club_a,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )
        self.perfil_b = PerfilUsuario.objects.create(
            usuario=self.admin_b,
            club=self.club_b,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.turno_a = TurnoClub.objects.create(
            club=self.club_a,
            dia_semana=0,
            nombre="Turno Club A",
            hora_inicio=time(15, 0),
            hora_fin=time(17, 0),
            orden=1,
            activo=True,
        )
        self.turno_b = TurnoClub.objects.create(
            club=self.club_b,
            dia_semana=0,
            nombre="Turno Club B",
            hora_inicio=time(18, 0),
            hora_fin=time(20, 0),
            orden=1,
            activo=True,
        )

        self.client.force_login(self.admin_a)

    def test_lista_turnos_no_muestra_turnos_de_otro_club(self):
        response = self.client.get(reverse("lista_turnos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Turno Club A")
        self.assertNotContains(response, "Turno Club B")

    def test_admin_no_puede_editar_turno_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_turno",
                kwargs={"turno_id": self.turno_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_no_puede_eliminar_turno_de_otro_club(self):
        response = self.client.post(
            reverse(
                "eliminar_turno",
                kwargs={"turno_id": self.turno_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            TurnoClub.objects.filter(pk=self.turno_b.pk).exists()
        )

    def test_lista_usuarios_no_muestra_usuarios_de_otro_club(self):
        response = self.client.get(reverse("lista_usuarios"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin_a.username)
        self.assertNotContains(response, self.admin_b.username)

    def test_admin_no_puede_editar_usuario_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_usuario",
                kwargs={"perfil_id": self.perfil_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_no_puede_cambiar_estado_usuario_de_otro_club(self):
        activo_antes = self.perfil_b.activo
        user_activo_antes = self.admin_b.is_active

        response = self.client.post(
            reverse(
                "cambiar_estado_usuario",
                kwargs={"perfil_id": self.perfil_b.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.perfil_b.refresh_from_db()
        self.admin_b.refresh_from_db()

        self.assertEqual(self.perfil_b.activo, activo_antes)
        self.assertEqual(self.admin_b.is_active, user_activo_antes)
