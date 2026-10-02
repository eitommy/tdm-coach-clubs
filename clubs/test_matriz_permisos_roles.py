from datetime import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clubs.models import Club, PerfilUsuario, TurnoClub
from asistencia.models import (
    CategoriaEjercicio,
    Ejercicio,
    Jugador,
)


class MatrizPermisosRolesTests(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nombre="Club Permisos",
            activo=True,
        )

        self.admin = User.objects.create_user(
            username="admin_permisos",
            password="TestPass123!",
            first_name="Admin",
            last_name="Permisos",
            is_active=True,
        )

        self.perfil_admin = PerfilUsuario.objects.create(
            usuario=self.admin,
            club=self.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
        )

        self.entrenador = User.objects.create_user(
            username="entrenador_permisos",
            password="TestPass123!",
            first_name="Entrenador",
            last_name="Permisos",
            is_active=True,
        )

        self.perfil_entrenador = PerfilUsuario.objects.create(
            usuario=self.entrenador,
            club=self.club,
            rol=PerfilUsuario.Rol.ENTRENADOR,
            activo=True,
        )

        self.turno = TurnoClub.objects.create(
            club=self.club,
            dia_semana=0,
            nombre="Turno prueba",
            hora_inicio=time(15, 0),
            hora_fin=time(17, 0),
            orden=1,
            activo=True,
        )

        self.jugador = Jugador.objects.create(
            club=self.club,
            nombre="Jugador",
            apellido="Prueba",
            activo=True,
        )

        self.categoria = CategoriaEjercicio.objects.create(
            club=self.club,
            nombre="Categoría prueba",
            orden=1,
            activo=True,
        )

        self.ejercicio = Ejercicio.objects.create(
            club=self.club,
            nombre="Ejercicio prueba",
            categoria_config=self.categoria,
            activo=True,
        )

    def _login_admin(self):
        self.client.force_login(
            self.admin
        )

    def _login_entrenador(self):
        self.client.force_login(
            self.entrenador
        )

    def test_entrenador_no_puede_entrar_a_rutas_exclusivas_admin_get(self):
        self._login_entrenador()

        rutas = [
            (
                "configuracion_club",
                {},
            ),
            (
                "lista_usuarios",
                {},
            ),
            (
                "crear_usuario",
                {},
            ),
            (
                "editar_usuario",
                {
                    "perfil_id":
                        self.perfil_admin.id
                },
            ),
        ]

        for nombre_url, kwargs in rutas:
            with self.subTest(
                nombre_url=nombre_url
            ):
                response = self.client.get(
                    reverse(
                        nombre_url,
                        kwargs=kwargs or None,
                    )
                )

                self.assertEqual(
                    response.status_code,
                    403,
                    msg=(
                        f'El entrenador accedió a '
                        f'"{nombre_url}" '
                        f"con status "
                        f"{response.status_code}."
                    ),
                )

    def test_entrenador_puede_entrar_a_rutas_operativas_get(self):
        self._login_entrenador()

        rutas = [
            (
                "lista_turnos",
                {},
            ),
            (
                "crear_turno",
                {},
            ),
            (
                "editar_turno",
                {
                    "turno_id":
                        self.turno.id
                },
            ),
            (
                "lista_jugadores",
                {},
            ),
            (
                "crear_jugador",
                {},
            ),
            (
                "editar_jugador",
                {
                    "pk":
                        self.jugador.id
                },
            ),
            (
                "lista_ejercicios",
                {},
            ),
            (
                "lista_categorias_ejercicio",
                {},
            ),
            (
                "crear_categoria_ejercicio",
                {},
            ),
            (
                "editar_categoria_ejercicio",
                {
                    "pk":
                        self.categoria.id
                },
            ),
            (
                "crear_ejercicio",
                {},
            ),
            (
                "editar_ejercicio",
                {
                    "pk":
                        self.ejercicio.id
                },
            ),
            (
                "seguimiento_semanal",
                {},
            ),
            (
                "reportes",
                {},
            ),
            (
                "dashboard_mensual",
                {},
            ),
            (
                "resumen_dia",
                {},
            ),
        ]

        for nombre_url, kwargs in rutas:
            with self.subTest(
                nombre_url=nombre_url
            ):
                response = self.client.get(
                    reverse(
                        nombre_url,
                        kwargs=kwargs or None,
                    )
                )

                self.assertEqual(
                    response.status_code,
                    200,
                    msg=(
                        f'El entrenador no pudo '
                        f'acceder a "{nombre_url}". '
                        f"Status: "
                        f"{response.status_code}."
                    ),
                )

    def test_entrenador_no_puede_ejecutar_acciones_exclusivas_admin_post(self):
        self._login_entrenador()

        perfil_activo_antes = (
            self.perfil_admin.activo
        )

        usuario_activo_antes = (
            self.admin.is_active
        )

        response = self.client.post(
            reverse(
                "cambiar_estado_usuario",
                kwargs={
                    "perfil_id":
                        self.perfil_admin.id
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.perfil_admin.refresh_from_db()
        self.admin.refresh_from_db()

        self.assertEqual(
            self.perfil_admin.activo,
            perfil_activo_antes,
        )

        self.assertEqual(
            self.admin.is_active,
            usuario_activo_antes,
        )

    def test_entrenador_puede_eliminar_turno_de_su_club(self):
        self._login_entrenador()

        turno = TurnoClub.objects.create(
            club=self.club,
            dia_semana=1,
            nombre="Turno eliminable",
            hora_inicio=time(18, 0),
            hora_fin=time(20, 0),
            orden=1,
            activo=True,
        )

        response = self.client.post(
            reverse(
                "eliminar_turno",
                kwargs={
                    "turno_id":
                        turno.id
                },
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            TurnoClub.objects.filter(
                pk=turno.id,
            ).exists()
        )

    def test_admin_puede_entrar_a_todas_las_rutas_de_gestion(self):
        self._login_admin()

        rutas = [
            (
                "configuracion_club",
                {},
            ),
            (
                "lista_turnos",
                {},
            ),
            (
                "crear_turno",
                {},
            ),
            (
                "editar_turno",
                {
                    "turno_id":
                        self.turno.id
                },
            ),
            (
                "lista_usuarios",
                {},
            ),
            (
                "crear_usuario",
                {},
            ),
            (
                "editar_usuario",
                {
                    "perfil_id":
                        self.perfil_entrenador.id
                },
            ),
            (
                "lista_jugadores",
                {},
            ),
            (
                "crear_jugador",
                {},
            ),
            (
                "editar_jugador",
                {
                    "pk":
                        self.jugador.id
                },
            ),
            (
                "lista_ejercicios",
                {},
            ),
            (
                "lista_categorias_ejercicio",
                {},
            ),
            (
                "crear_categoria_ejercicio",
                {},
            ),
            (
                "editar_categoria_ejercicio",
                {
                    "pk":
                        self.categoria.id
                },
            ),
            (
                "crear_ejercicio",
                {},
            ),
            (
                "editar_ejercicio",
                {
                    "pk":
                        self.ejercicio.id
                },
            ),
        ]

        for nombre_url, kwargs in rutas:
            with self.subTest(
                nombre_url=nombre_url
            ):
                response = self.client.get(
                    reverse(
                        nombre_url,
                        kwargs=kwargs or None,
                    )
                )

                self.assertEqual(
                    response.status_code,
                    200,
                    msg=(
                        f'El admin no pudo acceder '
                        f'a "{nombre_url}". '
                        f"Status: "
                        f"{response.status_code}."
                    ),
                )

    def test_entrenador_puede_acceder_a_historial_de_su_club(self):
        self._login_entrenador()

        response = self.client.get(
            reverse(
                "historial_jugador",
                kwargs={
                    "jugador_id":
                        self.jugador.id
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )