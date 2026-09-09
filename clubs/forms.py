from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Club, PerfilUsuario, TurnoClub


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            "nombre",
            "logo",
            "color_primario",
            "color_secundario",
            "email",
            "telefono",
            "direccion",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "color_primario": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                }
            ),
            "color_secundario": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                }
            ),
            "logo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class TurnoClubForm(forms.ModelForm):
    def __init__(
        self,
        *args,
        club=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.club = club

        if (
            self.club is None
            and self.instance
            and self.instance.pk
        ):
            self.club = self.instance.club

    class Meta:
        model = TurnoClub
        fields = [
            "dia_semana",
            "nombre",
            "hora_inicio",
            "hora_fin",
            "orden",
            "activo",
        ]

        widgets = {
            "dia_semana": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Turno mañana",
                }
            ),
            "hora_inicio": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "hora_fin": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "orden": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()

        if not nombre:
            raise forms.ValidationError(
                "El nombre del turno es obligatorio."
            )

        return nombre

    def clean(self):
        cleaned_data = super().clean()

        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")
        dia_semana = cleaned_data.get("dia_semana")
        orden = cleaned_data.get("orden")

        if (
            hora_inicio
            and hora_fin
            and hora_fin <= hora_inicio
        ):
            self.add_error(
                "hora_fin",
                "La hora de fin debe ser posterior a la hora de inicio.",
            )

        # El modelo tiene una restricción única por
        # club + día + orden. Como `club` no forma parte del formulario,
        # la validamos explícitamente antes de llegar a la base.
        if (
            self.club
            and dia_semana is not None
            and orden is not None
        ):
            turnos_duplicados = TurnoClub.objects.filter(
                club=self.club,
                dia_semana=dia_semana,
                orden=orden,
            )

            if self.instance and self.instance.pk:
                turnos_duplicados = turnos_duplicados.exclude(
                    pk=self.instance.pk,
                )

            if turnos_duplicados.exists():
                self.add_error(
                    "orden",
                    (
                        "Ya existe un turno con ese número de orden "
                        "para ese día."
                    ),
                )

        return cleaned_data


class UsuarioClubForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ej: matias",
                "autocomplete": "username",
            }
        ),
    )

    nombre = forms.CharField(
        label="Nombre",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "given-name",
            }
        ),
    )

    apellido = forms.CharField(
        label="Apellido",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "family-name",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    rol = forms.ChoiceField(
        label="Rol",
        choices=PerfilUsuario.Rol.choices,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    password_confirmacion = forms.CharField(
        label="Repetir contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username__iexact=username,
        ).exists():
            raise forms.ValidationError(
                "Ya existe un usuario con ese nombre."
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirmacion = cleaned_data.get(
            "password_confirmacion"
        )

        if (
            password
            and password_confirmacion
            and password != password_confirmacion
        ):
            self.add_error(
                "password_confirmacion",
                "Las contraseñas no coinciden.",
            )

        if password:
            usuario_temporal = User(
                username=cleaned_data.get("username", ""),
                first_name=cleaned_data.get("nombre", ""),
                last_name=cleaned_data.get("apellido", ""),
                email=cleaned_data.get("email", ""),
            )

            try:
                validate_password(
                    password,
                    user=usuario_temporal,
                )
            except ValidationError as error:
                for mensaje in error.messages:
                    self.add_error(
                        "password",
                        mensaje,
                    )

        return cleaned_data


class EditarUsuarioClubForm(forms.Form):
    nueva_password = forms.CharField(
        label="Nueva contraseña",
        required=False,
        strip=False,
        help_text=(
            "Dejala vacía si no querés cambiar la contraseña."
        ),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    nueva_password_confirmacion = forms.CharField(
        label="Repetir nueva contraseña",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    nombre = forms.CharField(
        label="Nombre",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "given-name",
            }
        ),
    )

    apellido = forms.CharField(
        label="Apellido",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "family-name",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    rol = forms.ChoiceField(
        label="Rol",
        choices=PerfilUsuario.Rol.choices,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    activo = forms.BooleanField(
        label="Activo",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    def __init__(
        self,
        *args,
        usuario=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("nueva_password")
        confirmacion = cleaned_data.get(
            "nueva_password_confirmacion"
        )

        if bool(password) != bool(confirmacion):
            self.add_error(
                "nueva_password_confirmacion",
                "Completá ambos campos de contraseña.",
            )
            return cleaned_data

        if password and password != confirmacion:
            self.add_error(
                "nueva_password_confirmacion",
                "Las contraseñas no coinciden.",
            )
            return cleaned_data

        if password:
            try:
                validate_password(
                    password,
                    user=self.usuario,
                )
            except ValidationError as error:
                for mensaje in error.messages:
                    self.add_error(
                        "nueva_password",
                        mensaje,
                    )

        return cleaned_data
