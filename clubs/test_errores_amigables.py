from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from clubs.models import Club, PerfilUsuario


@override_settings(DEBUG=False)
class ErroresAmigablesTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Errores",
            activo=True,
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_errores",
            password="ClaveErrores2026!",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

    def test_404_usa_pantalla_amigable(self):
        response = self.client.get(
            "/pagina-que-no-existe-tdm/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertContains(
            response,
            "No encontramos esa página",
            status_code=404,
        )

    def test_403_usa_pantalla_amigable(self):
        self.client.force_login(
            self.entrenador,
        )

        response = self.client.get(
            reverse("onboarding_club")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertContains(
            response,
            "No tenés permiso para entrar acá",
            status_code=403,
        )

    def test_handler500_devuelve_pantalla_amigable(self):
        from tdm_asistencia.error_views import error_500

        request = RequestFactory().get(
            "/error-prueba/"
        )

        request.user = AnonymousUser()

        response = error_500(request)

        self.assertEqual(
            response.status_code,
            500,
        )

        self.assertIn(
            "Ocurrió un error inesperado",
            response.content.decode("utf-8"),
        )
