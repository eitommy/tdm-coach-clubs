from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from clubs.models import Club, PagoClub


class PagoClubTests(TestCase):

    def setUp(self):
        self.hoy = timezone.localdate()

        self.club = Club.objects.create(
            nombre="Club Pagos",
            activo=True,
        )

    # ============================================================
    # REGISTRAR PAGO
    # ============================================================

    def test_registrar_pago_vigente_actualiza_club(self):
        periodo_hasta = (
            self.hoy
            + timedelta(days=30)
        )

        PagoClub.objects.create(
            club=self.club,
            periodo_desde=self.hoy,
            periodo_hasta=periodo_hasta,
            metodo_pago=PagoClub.MetodoPago.TRANSFERENCIA,
            referencia="Pago vigente",
        )

        self.club.refresh_from_db()

        self.assertEqual(
            self.club.pagado_hasta,
            periodo_hasta,
        )

        self.assertEqual(
            self.club.estado_pago,
            Club.EstadoPago.AL_DIA,
        )

        self.assertEqual(
            self.club.estado_pago_actual,
            Club.EstadoPago.AL_DIA,
        )

        self.assertFalse(
            self.club.suscripcion_bloqueada
        )

    # ============================================================
    # VARIOS PAGOS
    # ============================================================

    def test_varios_pagos_toman_periodo_mas_lejano(self):
        periodo_largo = (
            self.hoy
            + timedelta(days=60)
        )

        periodo_corto = (
            self.hoy
            + timedelta(days=30)
        )

        # Creamos primero el pago que cubre más tiempo.
        PagoClub.objects.create(
            club=self.club,
            periodo_desde=self.hoy,
            periodo_hasta=periodo_largo,
            referencia="Pago largo",
        )

        # Creamos después uno más corto para comprobar
        # que no se usa simplemente el último creado.
        PagoClub.objects.create(
            club=self.club,
            periodo_desde=self.hoy,
            periodo_hasta=periodo_corto,
            referencia="Pago corto",
        )

        self.club.refresh_from_db()

        self.assertEqual(
            self.club.pagado_hasta,
            periodo_largo,
        )

        self.assertEqual(
            self.club.estado_pago,
            Club.EstadoPago.AL_DIA,
        )

    # ============================================================
    # ELIMINAR PAGO
    # ============================================================

    def test_eliminar_ultimo_periodo_restaura_pago_anterior(self):
        periodo_anterior = (
            self.hoy
            + timedelta(days=30)
        )

        periodo_nuevo = (
            self.hoy
            + timedelta(days=60)
        )

        PagoClub.objects.create(
            club=self.club,
            periodo_desde=self.hoy,
            periodo_hasta=periodo_anterior,
            referencia="Pago anterior",
        )

        pago_nuevo = PagoClub.objects.create(
            club=self.club,
            periodo_desde=(
                self.hoy
                + timedelta(days=31)
            ),
            periodo_hasta=periodo_nuevo,
            referencia="Pago nuevo",
        )

        self.club.refresh_from_db()

        self.assertEqual(
            self.club.pagado_hasta,
            periodo_nuevo,
        )

        pago_nuevo.delete()

        self.club.refresh_from_db()

        self.assertEqual(
            self.club.pagado_hasta,
            periodo_anterior,
        )

        self.assertEqual(
            self.club.estado_pago,
            Club.EstadoPago.AL_DIA,
        )

    # ============================================================
    # DESBLOQUEO AUTOMÁTICO
    # ============================================================

    def test_pago_nuevo_desbloquea_club_vencido(self):
        self.club.pagado_hasta = (
            self.hoy
            - timedelta(days=8)
        )

        self.club.estado_pago = (
            Club.EstadoPago.VENCIDO
        )

        self.club.save(
            update_fields=[
                "pagado_hasta",
                "estado_pago",
            ]
        )

        self.assertTrue(
            self.club.suscripcion_bloqueada
        )

        nuevo_periodo_hasta = (
            self.hoy
            + timedelta(days=30)
        )

        PagoClub.objects.create(
            club=self.club,
            periodo_desde=self.hoy,
            periodo_hasta=nuevo_periodo_hasta,
            metodo_pago=PagoClub.MetodoPago.TRANSFERENCIA,
            referencia="Regularización",
        )

        self.club.refresh_from_db()

        self.assertEqual(
            self.club.pagado_hasta,
            nuevo_periodo_hasta,
        )

        self.assertEqual(
            self.club.estado_pago_actual,
            Club.EstadoPago.AL_DIA,
        )

        self.assertFalse(
            self.club.suscripcion_bloqueada
        )