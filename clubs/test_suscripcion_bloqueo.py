from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clubs.models import Club, PerfilUsuario


class SuscripcionClubTests(TestCase):

    def setUp(self):
        self.hoy = timezone.localdate()

        self.club = Club.objects.create(
            nombre="Club Suscripción",
            activo=True,
        )

        self.admin = User.objects.create_user(
            username="admin_suscripcion",
            password="TestPass123!",
            first_name="Admin",
            last_name="Suscripción",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_suscripcion",
            password="TestPass123!",
            first_name="Entrenador",
            last_name="Suscripción",
            is_active=True,
        )

        PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

    # ============================================================
    # LÓGICA DEL MODELO
    # ============================================================

    def test_club_sin_pago_no_se_bloquea(self):
        self.club.pagado_hasta = None

        self.assertEqual(
            self.club.estado_pago_actual,
            Club.EstadoPago.PENDIENTE,
        )

        self.assertEqual(
            self.club.dias_vencido,
            0,
        )

        self.assertFalse(
            self.club.en_periodo_gracia_pago
        )

        self.assertFalse(
            self.club.suscripcion_bloqueada
        )

    def test_club_al_dia_no_se_bloquea(self):
        self.club.pagado_hasta = self.hoy

        self.assertEqual(
            self.club.estado_pago_actual,
            Club.EstadoPago.AL_DIA,
        )

        self.assertEqual(
            self.club.dias_vencido,
            0,
        )

        self.assertFalse(
            self.club.en_periodo_gracia_pago
        )

        self.assertFalse(
            self.club.suscripcion_bloqueada
        )

    def test_primer_dia_vencido_esta_en_gracia(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=1)
        )

        self.assertEqual(
            self.club.estado_pago_actual,
            Club.EstadoPago.VENCIDO,
        )

        self.assertEqual(
            self.club.dias_vencido,
            1,
        )

        self.assertTrue(
            self.club.en_periodo_gracia_pago
        )

        self.assertEqual(
            self.club.dias_hasta_bloqueo,
            7,
        )

        self.assertFalse(
            self.club.suscripcion_bloqueada
        )

    def test_dia_siete_vencido_sigue_en_gracia(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=7)
        )

        self.assertEqual(
            self.club.dias_vencido,
            7,
        )

        self.assertTrue(
            self.club.en_periodo_gracia_pago
        )

        self.assertEqual(
            self.club.dias_hasta_bloqueo,
            1,
        )

        self.assertFalse(
            self.club.suscripcion_bloqueada
        )

    def test_dia_ocho_vencido_bloquea(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=8)
        )

        self.assertEqual(
            self.club.dias_vencido,
            8,
        )

        self.assertFalse(
            self.club.en_periodo_gracia_pago
        )

        self.assertEqual(
            self.club.dias_hasta_bloqueo,
            0,
        )

        self.assertTrue(
            self.club.suscripcion_bloqueada
        )

    # ============================================================
    # AVISO DURANTE EL PERÍODO DE GRACIA
    # ============================================================

    def test_periodo_gracia_muestra_aviso_sin_bloquear(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=3)
        )

        self.club.save(
            update_fields=[
                "pagado_hasta",
            ]
        )

        self.client.force_login(
            self.admin
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
            "Suscripción vencida",
        )

        contenido = " ".join(
            response.content.decode().split()
        )

        self.assertIn(
            "5 días más",
            contenido,
        )

    # ============================================================
    # BLOQUEO - ADMIN
    # ============================================================

    def test_admin_bloqueado_no_puede_usar_area_operativa(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=8)
        )

        self.club.save(
            update_fields=[
                "pagado_hasta",
            ]
        )

        self.client.force_login(
            self.admin
        )

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertContains(
            response,
            "El acceso al club está temporalmente bloqueado",
            status_code=403,
        )

        self.assertContains(
            response,
            "Ver suscripción",
            status_code=403,
        )

    def test_admin_bloqueado_puede_ver_configuracion(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=8)
        )

        self.club.save(
            update_fields=[
                "pagado_hasta",
            ]
        )

        self.client.force_login(
            self.admin
        )

        response = self.client.get(
            reverse(
                "configuracion_club"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Vencido",
        )

        self.assertContains(
            response,
            "Estado del servicio",
        )

    # ============================================================
    # BLOQUEO - ENTRENADOR
    # ============================================================

    def test_entrenador_bloqueado_no_puede_usar_area_operativa(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=8)
        )

        self.club.save(
            update_fields=[
                "pagado_hasta",
            ]
        )

        self.client.force_login(
            self.entrenador
        )

        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertContains(
            response,
            "El acceso al club está temporalmente bloqueado",
            status_code=403,
        )

        self.assertContains(
            response,
            "Contactá al administrador del club",
            status_code=403,
        )

        self.assertNotContains(
            response,
            "Ver suscripción",
            status_code=403,
        )

    def test_entrenador_bloqueado_no_puede_entrar_a_configuracion(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=8)
        )

        self.club.save(
            update_fields=[
                "pagado_hasta",
            ]
        )

        self.client.force_login(
            self.entrenador
        )

        response = self.client.get(
            reverse(
                "configuracion_club"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertContains(
            response,
            "El acceso al club está temporalmente bloqueado",
            status_code=403,
        )

        self.assertNotContains(
            response,
            "Ver suscripción",
            status_code=403,
        )