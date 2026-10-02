from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario
from asistencia.models import CategoriaEjercicio, Ejercicio, Jugador


class SeguridadMulticlubCatalogosTests(TestCase):
    def setUp(self):
        self.club_a = Club.objects.create(nombre="Club A")
        self.club_b = Club.objects.create(nombre="Club B")

        self.admin_a = User.objects.create_user(
            username="admin_a_catalogos",
            password="TestPass123!",
        )
        self.admin_b = User.objects.create_user(
            username="admin_b_catalogos",
            password="TestPass123!",
        )

        PerfilUsuario.objects.create(
            usuario=self.admin_a,
            club=self.club_a,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )
        PerfilUsuario.objects.create(
            usuario=self.admin_b,
            club=self.club_b,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.jugador_a = Jugador.objects.create(
            club=self.club_a,
            nombre="Jugador",
            apellido="Club A",
            activo=True,
        )
        self.jugador_b = Jugador.objects.create(
            club=self.club_b,
            nombre="Jugador",
            apellido="Club B",
            activo=True,
        )

        self.categoria_a = CategoriaEjercicio.objects.create(
            club=self.club_a,
            nombre="Categoría A",
            orden=1,
            activo=True,
        )
        self.categoria_b = CategoriaEjercicio.objects.create(
            club=self.club_b,
            nombre="Categoría B",
            orden=1,
            activo=True,
        )

        self.ejercicio_a = Ejercicio.objects.create(
            club=self.club_a,
            categoria_config=self.categoria_a,
            nombre="Ejercicio Club A",
            activo=True,
        )
        self.ejercicio_b = Ejercicio.objects.create(
            club=self.club_b,
            categoria_config=self.categoria_b,
            nombre="Ejercicio Club B",
            activo=True,
        )

        self.client.force_login(self.admin_a)

    def test_lista_jugadores_no_filtra_datos_de_otro_club(self):
        response = self.client.get(reverse("lista_jugadores"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Club A")
        self.assertNotContains(response, "Club B")

    def test_no_puede_editar_jugador_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_jugador",
                kwargs={"pk": self.jugador_b.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_historial_jugador_de_otro_club_no_es_accesible(self):
        response = self.client.get(
            reverse(
                "historial_jugador",
                kwargs={"jugador_id": self.jugador_b.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_lista_ejercicios_no_filtra_datos_de_otro_club(self):
        response = self.client.get(reverse("lista_ejercicios"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ejercicio Club A")
        self.assertNotContains(response, "Ejercicio Club B")

    def test_no_puede_editar_ejercicio_de_otro_club(self):
        response = self.client.get(
            reverse(
                "editar_ejercicio",
                kwargs={"pk": self.ejercicio_b.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_form_ejercicio_no_ofrece_categorias_de_otro_club(self):
        response = self.client.get(reverse("crear_ejercicio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Categoría A")
        self.assertNotContains(response, "Categoría B")
