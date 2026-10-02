from django.contrib.auth.models import User
from django.test import TestCase

from clubs.forms import EditarUsuarioClubForm, UsuarioClubForm
from clubs.models import PerfilUsuario


class EmailUsuariosClubTests(TestCase):
    def setUp(self):
        self.password = "PruebaSegura123!"
        self.usuario_existente = User.objects.create_user(
            username="existente",
            email="existente@example.com",
            password=self.password,
        )

    def datos_creacion(self, **overrides):
        datos = {
            "username": "nuevo_usuario",
            "nombre": "Nuevo",
            "apellido": "Usuario",
            "email": "nuevo@example.com",
            "rol": PerfilUsuario.Rol.ENTRENADOR,
            "password": self.password,
            "password_confirmacion": self.password,
        }
        datos.update(overrides)
        return datos

    def datos_edicion(self, **overrides):
        datos = {
            "nombre": "Usuario",
            "apellido": "Existente",
            "email": "existente@example.com",
            "rol": PerfilUsuario.Rol.ENTRENADOR,
            "activo": "on",
            "nueva_password": "",
            "nueva_password_confirmacion": "",
        }
        datos.update(overrides)
        return datos

    def test_crear_usuario_exige_email(self):
        form = UsuarioClubForm(
            data=self.datos_creacion(email="")
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_crear_usuario_rechaza_email_duplicado_sin_importar_mayusculas(self):
        form = UsuarioClubForm(
            data=self.datos_creacion(
                email="EXISTENTE@example.com"
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_editar_usuario_permite_conservar_su_propio_email(self):
        form = EditarUsuarioClubForm(
            data=self.datos_edicion(),
            usuario=self.usuario_existente,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

    def test_editar_usuario_rechaza_email_de_otro_usuario(self):
        otro = User.objects.create_user(
            username="otro",
            email="otro@example.com",
            password=self.password,
        )

        form = EditarUsuarioClubForm(
            data=self.datos_edicion(
                email=otro.email,
            ),
            usuario=self.usuario_existente,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_se_normaliza_a_minusculas(self):
        form = UsuarioClubForm(
            data=self.datos_creacion(
                email="Nuevo.Usuario@Example.COM",
            )
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )
        self.assertEqual(
            form.cleaned_data["email"],
            "nuevo.usuario@example.com",
        )
