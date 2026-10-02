from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub


class OnboardingClubTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Onboarding",
            activo=True,
        )

        self.admin = User.objects.create_user(
            username="admin_onboarding",
            password="ClaveAdmin2026!",
            is_active=True,
        )

        self.perfil_admin = PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.client.force_login(
            self.admin,
        )

    def test_admin_puede_ver_onboarding(self):
        response = self.client.get(
            reverse("onboarding_club")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "Primeros pasos en Club Onboarding",
        )
        self.assertContains(
            response,
            "1 de 6 completados",
        )

    def test_turno_actualiza_progreso(self):
        TurnoClub.objects.create(
            club=self.club,
            dia_semana=TurnoClub.DiaSemana.LUNES,
            nombre="Turno mañana",
            orden=1,
            activo=True,
        )

        response = self.client.get(
            reverse("onboarding_club")
        )

        self.assertContains(
            response,
            "2 de 6 completados",
        )

    def test_entrenador_actualiza_progreso(self):
        entrenador = User.objects.create_user(
            username="entrenador_onboarding",
            password="ClaveEntrenador2026!",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        response = self.client.get(
            reverse("onboarding_club")
        )

        self.assertContains(
            response,
            "2 de 6 completados",
        )

    def test_entrenador_no_puede_ver_onboarding_admin(self):
        entrenador = User.objects.create_user(
            username="solo_entrenador",
            password="ClaveEntrenador2026!",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.client.force_login(
            entrenador,
        )

        response = self.client.get(
            reverse("onboarding_club")
        )

        self.assertEqual(
            response.status_code,
            403,
        )
