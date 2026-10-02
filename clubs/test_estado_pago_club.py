from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.forms import ClubForm
from clubs.models import Club, PerfilUsuario


class EstadoPagoClubTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Pago",
            email="club@example.com",
            telefono="1234",
            direccion="Dirección inicial",
            activo=True,
            estado_pago=Club.EstadoPago.AL_DIA,
            pagado_hasta=date(2026, 10, 31),
            observacion_pago="Nota interna que no debe mostrarse.",
        )

        self.admin = User.objects.create_user(
            username="admin_pago",
            password="TestPass123!",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.client.force_login(self.admin)

    def test_configuracion_muestra_estado_y_fecha_pago(self):
        response = self.client.get(
            reverse("configuracion_club")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Suscripción")
        self.assertContains(response, "Al día")
        self.assertContains(response, "31/10/2026")

    def test_configuracion_no_muestra_observacion_interna_pago(self):
        response = self.client.get(
            reverse("configuracion_club")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Nota interna que no debe mostrarse.",
        )

    def test_formulario_club_no_expone_campos_de_pago(self):
        form = ClubForm(instance=self.club)

        self.assertNotIn("estado_pago", form.fields)
        self.assertNotIn("pagado_hasta", form.fields)
        self.assertNotIn("observacion_pago", form.fields)

    def test_post_manipulado_no_puede_cambiar_datos_de_pago(self):
        response = self.client.post(
            reverse("configuracion_club"),
            data={
                "nombre": "Club Pago Editado",
                "color_primario": "#112233",
                "color_secundario": "#445566",
                "email": "nuevo@example.com",
                "telefono": "9999",
                "direccion": "Nueva dirección",
                # Intento de manipular campos que no pertenecen al form.
                "estado_pago": Club.EstadoPago.VENCIDO,
                "pagado_hasta": "2020-01-01",
                "observacion_pago": "Intento de sobrescritura",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.club.refresh_from_db()

        # Los campos editables sí cambian.
        self.assertEqual(self.club.nombre, "Club Pago Editado")
        self.assertEqual(self.club.email, "nuevo@example.com")

        # Los campos de pago quedan intactos.
        self.assertEqual(
            self.club.estado_pago,
            Club.EstadoPago.AL_DIA,
        )
        self.assertEqual(
            self.club.pagado_hasta,
            date(2026, 10, 31),
        )
        self.assertEqual(
            self.club.observacion_pago,
            "Nota interna que no debe mostrarse.",
        )
