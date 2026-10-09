from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from asistencia.models import Asistencia, Entrenamiento, Jugador
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

    def crear_turno_para_fecha(
        self,
        fecha=None,
        nombre="Turno prueba",
        orden=1,
    ):
        if fecha is None:
            fecha = timezone.localdate()

        return TurnoClub.objects.create(
            club=self.club,
            dia_semana=fecha.weekday(),
            nombre=nombre,
            orden=orden,
            activo=True,
        )

    def crear_entrenamiento_valido(
        self,
        turno,
        fecha=None,
    ):
        if fecha is None:
            fecha = timezone.localdate()

        entrenamiento = Entrenamiento.objects.create(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
            responsable_usuario=self.admin,
        )

        jugador = Jugador.objects.create(
            club=self.club,
            nombre="Jugador",
            apellido="Prueba",
            activo=True,
        )

        Asistencia.objects.create(
            entrenamiento=entrenamiento,
            jugador=jugador,
            estado="asistio",
        )

        return entrenamiento

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

    def test_inicio_detecta_onboarding_por_querystring(self):
        response = self.client.get(
            reverse("inicio") + "?onboarding=1"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.context["viene_de_onboarding"]
        )

    def test_inicio_normal_no_activa_onboarding(self):
        response = self.client.get(
            reverse("inicio")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.context["viene_de_onboarding"]
        )

    def test_dia_turno_guarda_entrenamiento_onboarding_en_sesion(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        url = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha.isoformat(),
                "turno_id": turno.id,
            },
        )

        response = self.client.get(
            url + "?onboarding=1"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        entrenamiento = Entrenamiento.objects.get(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
        )

        self.assertEqual(
            self.client.session.get(
                "onboarding_entrenamiento_id"
            ),
            entrenamiento.id,
        )

        self.assertTrue(
            response.context["viene_de_onboarding"]
        )

    def test_dia_turno_mantiene_onboarding_sin_querystring(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        url = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha.isoformat(),
                "turno_id": turno.id,
            },
        )

        primera_response = self.client.get(
            url + "?onboarding=1"
        )

        self.assertEqual(
            primera_response.status_code,
            200,
        )

        entrenamiento = Entrenamiento.objects.get(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
        )

        segunda_response = self.client.get(
            url
        )

        self.assertEqual(
            segunda_response.status_code,
            200,
        )

        self.assertTrue(
            segunda_response.context[
                "viene_de_onboarding"
            ]
        )

        self.assertEqual(
            self.client.session.get(
                "onboarding_entrenamiento_id"
            ),
            entrenamiento.id,
        )

    def test_dia_turno_normal_no_activa_onboarding(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        url = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha.isoformat(),
                "turno_id": turno.id,
            },
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.context["viene_de_onboarding"]
        )

        self.assertNotIn(
            "onboarding_entrenamiento_id",
            self.client.session,
        )

    def test_otro_entrenamiento_no_hereda_onboarding(self):
        fecha = timezone.localdate()
        fecha_siguiente = fecha + timedelta(days=7)

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        url_original = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha.isoformat(),
                "turno_id": turno.id,
            },
        )

        response_original = self.client.get(
            url_original + "?onboarding=1"
        )

        self.assertEqual(
            response_original.status_code,
            200,
        )

        entrenamiento_original = Entrenamiento.objects.get(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
        )

        url_otro = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha_siguiente.isoformat(),
                "turno_id": turno.id,
            },
        )

        response_otro = self.client.get(
            url_otro
        )

        self.assertEqual(
            response_otro.status_code,
            200,
        )

        entrenamiento_otro = Entrenamiento.objects.get(
            club=self.club,
            fecha=fecha_siguiente,
            turno_config=turno,
        )

        self.assertNotEqual(
            entrenamiento_original.id,
            entrenamiento_otro.id,
        )

        self.assertFalse(
            response_otro.context[
                "viene_de_onboarding"
            ]
        )

        self.assertEqual(
            self.client.session.get(
                "onboarding_entrenamiento_id"
            ),
            entrenamiento_original.id,
        )

    def test_entrenamiento_no_finalizado_no_completa_ultimo_paso(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        Entrenamiento.objects.create(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
            finalizado=False,
        )

        response = self.client.get(
            reverse("onboarding_club")
        )

        ultimo_paso = response.context["pasos"][-1]

        self.assertFalse(
            ultimo_paso["completo"]
        )

    def test_entrenamiento_finalizado_completa_ultimo_paso(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        Entrenamiento.objects.create(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
            finalizado=True,
        )

        response = self.client.get(
            reverse("onboarding_club")
        )

        ultimo_paso = response.context["pasos"][-1]

        self.assertTrue(
            ultimo_paso["completo"]
        )

    def test_finalizar_entrenamiento_de_onboarding_vuelve_al_onboarding(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        url_dia = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha.isoformat(),
                "turno_id": turno.id,
            },
        )

        response_dia = self.client.get(
            url_dia + "?onboarding=1"
        )

        self.assertEqual(
            response_dia.status_code,
            200,
        )

        entrenamiento = Entrenamiento.objects.get(
            club=self.club,
            fecha=fecha,
            turno_config=turno,
        )

        entrenamiento.responsable_usuario = self.admin
        entrenamiento.save(
            update_fields=[
                "responsable_usuario",
            ]
        )

        jugador = Jugador.objects.create(
            club=self.club,
            nombre="Jugador",
            apellido="Onboarding",
            activo=True,
        )

        Asistencia.objects.create(
            entrenamiento=entrenamiento,
            jugador=jugador,
            estado="asistio",
        )

        self.assertEqual(
            self.client.session.get(
                "onboarding_entrenamiento_id"
            ),
            entrenamiento.id,
        )

        response = self.client.post(
            reverse(
                "finalizar_turno",
                kwargs={
                    "entrenamiento_id": entrenamiento.id,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse("onboarding_club"),
        )

        entrenamiento.refresh_from_db()

        self.assertTrue(
            entrenamiento.finalizado
        )

        self.assertNotIn(
            "onboarding_entrenamiento_id",
            self.client.session,
        )

        response_onboarding = self.client.get(
            reverse("onboarding_club")
        )

        ultimo_paso = response_onboarding.context[
            "pasos"
        ][-1]

        self.assertTrue(
            ultimo_paso["completo"]
        )

    def test_finalizar_entrenamiento_normal_vuelve_al_turno(self):
        fecha = timezone.localdate()

        turno = self.crear_turno_para_fecha(
            fecha=fecha,
        )

        entrenamiento = self.crear_entrenamiento_valido(
            turno=turno,
            fecha=fecha,
        )

        response = self.client.post(
            reverse(
                "finalizar_turno",
                kwargs={
                    "entrenamiento_id": entrenamiento.id,
                },
            )
        )

        url_esperada = reverse(
            "dia_turno",
            kwargs={
                "fecha_str": fecha.isoformat(),
                "turno_id": turno.id,
            },
        )

        self.assertRedirects(
            response,
            url_esperada,
        )

        entrenamiento.refresh_from_db()

        self.assertTrue(
            entrenamiento.finalizado
        )

        self.assertNotIn(
            "onboarding_entrenamiento_id",
            self.client.session,
        )