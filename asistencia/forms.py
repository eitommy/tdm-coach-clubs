from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import inlineformset_factory

from clubs.models import PerfilUsuario

from .models import (
    Jugador,
    Ejercicio,
    Entrenamiento,
    TrabajoTurno,
    Asistencia,
    ObservacionJugador,
    PartidoTurno,
    SetPartido,
)


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Email",
        }

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre",
                    "autocomplete": "off",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apellido",
                    "autocomplete": "off",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email",
                    "autocomplete": "off",
                }
            ),
        }


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador

        # El club NO se muestra en el formulario.
        # Se asignará desde request.user en la vista.
        fields = [
            "nombre",
            "apellido",
            "activo",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del jugador",
                    "autocomplete": "off",
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apellido del jugador",
                    "autocomplete": "off",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, club=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.club = club

    def clean_nombre(self):
        return self.cleaned_data.get(
            "nombre",
            "",
        ).strip()

    def clean_apellido(self):
        return self.cleaned_data.get(
            "apellido",
            "",
        ).strip()


class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio

        # El club se asignará desde la vista.
        fields = [
            "categoria",
            "nombre",
            "activo",
        ]

        widgets = {
            "categoria": forms.Select(
                attrs={
                    "class": "form-select",
                    "autocomplete": "off",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del ejercicio",
                    "autocomplete": "off",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, club=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.club = club

    def clean_nombre(self):
        nombre = self.cleaned_data.get(
            "nombre",
            "",
        ).strip()

        if not nombre:
            raise forms.ValidationError(
                "El nombre del ejercicio es obligatorio."
            )

        return nombre

    def clean(self):
        cleaned_data = super().clean()

        nombre = cleaned_data.get("nombre")
        categoria = cleaned_data.get("categoria")

        if not nombre or not categoria:
            return cleaned_data

        ejercicios = Ejercicio.objects.filter(
            nombre__iexact=nombre,
            categoria=categoria,
        )

        if self.club:
            ejercicios = ejercicios.filter(
                club=self.club,
            )

        if self.instance and self.instance.pk:
            ejercicios = ejercicios.exclude(
                pk=self.instance.pk,
            )

        if ejercicios.exists():
            raise forms.ValidationError(
                "Ya existe un ejercicio con ese nombre y categoría."
            )

        return cleaned_data


class EntrenamientoInfoForm(forms.ModelForm):
    class Meta:
        model = Entrenamiento

        fields = [
            "responsable_usuario",
            "observaciones",
        ]

        labels = {
            "responsable_usuario": "Entrenador responsable",
            "observaciones": "Observaciones",
        }

        widgets = {
            "responsable_usuario": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones del turno...",
                }
            ),
        }

    def __init__(
        self,
        *args,
        club=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "responsable_usuario"
        ].required = False

        self.club = club

        club_objetivo = club

        if (
            club_objetivo is None
            and self.instance
            and self.instance.pk
            and self.instance.club_id
        ):
            club_objetivo = self.instance.club

        usuarios = User.objects.none()

        if club_objetivo:
            usuarios = (
                User.objects
                .filter(
                    is_active=True,
                    perfil_club__club=club_objetivo,
                    perfil_club__activo=True,
                    perfil_club__rol__in=[
                        PerfilUsuario.Rol.ADMIN,
                        PerfilUsuario.Rol.ENTRENADOR,
                    ],
                )
                .distinct()
                .order_by(
                    "first_name",
                    "last_name",
                    "username",
                )
            )

        self.fields[
            "responsable_usuario"
        ].queryset = usuarios

        self.fields[
            "responsable_usuario"
        ].empty_label = "Seleccionar entrenador"

        self.fields[
            "responsable_usuario"
        ].label_from_instance = (
            lambda usuario: (
                usuario.get_full_name()
                or usuario.username
            )
        )

    def clean_responsable_usuario(self):
        usuario = self.cleaned_data.get(
            "responsable_usuario"
        )

        if not usuario:
            return usuario

        club_objetivo = self.club if hasattr(self, "club") else None

        if (
            club_objetivo is None
            and self.instance
            and self.instance.club_id
        ):
            club_objetivo = self.instance.club

        if club_objetivo:
            perfil = getattr(
                usuario,
                "perfil_club",
                None,
            )

            if (
                perfil is None
                or not perfil.activo
                or perfil.club_id != club_objetivo.id
                or perfil.rol not in [
                    PerfilUsuario.Rol.ADMIN,
                    PerfilUsuario.Rol.ENTRENADOR,
                ]
            ):
                raise forms.ValidationError(
                    "El responsable seleccionado no pertenece a este club."
                )

        return usuario


class NoEntrenamientoForm(forms.ModelForm):
    class Meta:
        model = Entrenamiento

        fields = [
            "no_se_entreno",
            "motivo_no_entrenamiento",
            "detalle_no_entrenamiento",
        ]

        labels = {
            "no_se_entreno": "No se entrenó",
            "motivo_no_entrenamiento": "Motivo",
            "detalle_no_entrenamiento": "Detalle opcional",
        }

        widgets = {
            "no_se_entreno": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "motivo_no_entrenamiento": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "detalle_no_entrenamiento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ejemplo: feriado nacional, torneo, "
                        "club cerrado..."
                    ),
                    "autocomplete": "off",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        no_se_entreno = cleaned_data.get(
            "no_se_entreno"
        )

        motivo = cleaned_data.get(
            "motivo_no_entrenamiento"
        )

        if no_se_entreno and not motivo:
            self.add_error(
                "motivo_no_entrenamiento",
                "Seleccioná un motivo.",
            )

        return cleaned_data


class TrabajoTurnoForm(forms.ModelForm):
    class Meta:
        model = TrabajoTurno

        fields = [
            "cambio",
            "tipo",
            "jugador_1",
            "jugador_2",
            "detalle",
        ]

        labels = {
            "cambio": "Cambio",
            "tipo": "Tipo de trabajo",
            "jugador_1": "Jugador",
            "jugador_2": "Compañero",
            "detalle": "Detalle opcional",
        }

        widgets = {
            "cambio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Ejemplo: 1",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_tipo_trabajo",
                }
            ),
            "jugador_1": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "jugador_2": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_jugador_2",
                }
            ),
            "detalle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ejemplo: saque y tercera pelota"
                    ),
                    "autocomplete": "off",
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.entrenamiento = kwargs.pop(
            "entrenamiento",
            None,
        )

        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "jugador_2"
        ].required = False

        self.fields[
            "detalle"
        ].required = False

        if not self.entrenamiento:
            self.fields[
                "jugador_1"
            ].queryset = Jugador.objects.none()

            self.fields[
                "jugador_2"
            ].queryset = Jugador.objects.none()

            return

        asistencias_turno = (
            Asistencia.objects
            .filter(
                entrenamiento=self.entrenamiento,
                estado__in=[
                    "asistio",
                    "tarde",
                ],
            )
            .select_related(
                "jugador"
            )
        )

        jugadores_ids = asistencias_turno.values_list(
            "jugador_id",
            flat=True,
        )

        jugadores_del_turno = Jugador.objects.filter(
            id__in=jugadores_ids,
            activo=True,
        )

        if self.entrenamiento.club_id:
            jugadores_del_turno = jugadores_del_turno.filter(
                club=self.entrenamiento.club,
            )

        jugadores_del_turno = jugadores_del_turno.order_by(
            "apellido",
            "nombre",
        )

        self.fields[
            "jugador_1"
        ].queryset = jugadores_del_turno

        self.fields[
            "jugador_2"
        ].queryset = jugadores_del_turno

        if self.is_bound:
            return

        trabajos = TrabajoTurno.objects.filter(
            entrenamiento=self.entrenamiento,
        )

        ultimo_cambio = (
            trabajos
            .order_by("-cambio")
            .values_list(
                "cambio",
                flat=True,
            )
            .first()
        )

        if ultimo_cambio is None:
            cambio_sugerido = 1

        else:
            trabajos_ultimo_cambio = trabajos.filter(
                cambio=ultimo_cambio,
            )

            jugadores_asignados_ids = set()

            for trabajo in trabajos_ultimo_cambio:
                jugadores_asignados_ids.add(
                    trabajo.jugador_1_id
                )

                if trabajo.jugador_2_id:
                    jugadores_asignados_ids.add(
                        trabajo.jugador_2_id
                    )

            jugadores_que_entrenaron_ids = set(
                asistencias_turno.values_list(
                    "jugador_id",
                    flat=True,
                )
            )

            total_jugadores = len(
                jugadores_que_entrenaron_ids
            )

            total_asignados = len(
                jugadores_asignados_ids
                & jugadores_que_entrenaron_ids
            )

            ultimo_cambio_completo = (
                total_jugadores > 0
                and total_asignados == total_jugadores
            )

            if ultimo_cambio_completo:
                cambio_sugerido = ultimo_cambio + 1
            else:
                cambio_sugerido = ultimo_cambio

        self.fields[
            "cambio"
        ].initial = cambio_sugerido

    def clean(self):
        cleaned_data = super().clean()

        cambio = cleaned_data.get(
            "cambio"
        )

        tipo = cleaned_data.get(
            "tipo"
        )

        jugador_1 = cleaned_data.get(
            "jugador_1"
        )

        jugador_2 = cleaned_data.get(
            "jugador_2"
        )

        if not self.entrenamiento:
            return cleaned_data

        if not cambio or not jugador_1:
            return cleaned_data

        jugadores_que_entrenaron_ids = set(
            Asistencia.objects
            .filter(
                entrenamiento=self.entrenamiento,
                estado__in=[
                    "asistio",
                    "tarde",
                ],
            )
            .values_list(
                "jugador_id",
                flat=True,
            )
        )

        if (
            jugador_1
            and jugador_1.id
            not in jugadores_que_entrenaron_ids
        ):
            self.add_error(
                "jugador_1",
                (
                    f"{jugador_1} no figura como "
                    "presente o tarde en este turno."
                ),
            )

        if (
            jugador_2
            and jugador_2.id
            not in jugadores_que_entrenaron_ids
        ):
            self.add_error(
                "jugador_2",
                (
                    f"{jugador_2} no figura como "
                    "presente o tarde en este turno."
                ),
            )

        # Validación extra de club.
        if self.entrenamiento.club_id:

            if (
                jugador_1
                and jugador_1.club_id
                != self.entrenamiento.club_id
            ):
                self.add_error(
                    "jugador_1",
                    (
                        "El jugador seleccionado no "
                        "pertenece a este club."
                    ),
                )

            if (
                jugador_2
                and jugador_2.club_id
                != self.entrenamiento.club_id
            ):
                self.add_error(
                    "jugador_2",
                    (
                        "El compañero seleccionado no "
                        "pertenece a este club."
                    ),
                )

        if tipo == TrabajoTurno.Tipo.PAREJA:

            if not jugador_2:
                self.add_error(
                    "jugador_2",
                    (
                        "Para una pareja tenés que "
                        "seleccionar un compañero."
                    ),
                )

                return cleaned_data

            if jugador_1 == jugador_2:
                self.add_error(
                    "jugador_2",
                    (
                        "Un jugador no puede formar "
                        "pareja consigo mismo."
                    ),
                )

                return cleaned_data

        else:
            jugador_2 = None
            cleaned_data[
                "jugador_2"
            ] = None

        trabajos_mismo_cambio = TrabajoTurno.objects.filter(
            entrenamiento=self.entrenamiento,
            cambio=cambio,
        )

        if (
            self.instance
            and self.instance.pk
        ):
            trabajos_mismo_cambio = (
                trabajos_mismo_cambio.exclude(
                    pk=self.instance.pk,
                )
            )

        jugador_1_ocupado = (
            trabajos_mismo_cambio.filter(
                Q(jugador_1=jugador_1)
                | Q(jugador_2=jugador_1)
            ).exists()
        )

        if jugador_1_ocupado:
            self.add_error(
                "jugador_1",
                (
                    f"{jugador_1} ya tiene una actividad "
                    f"cargada en el cambio {cambio}."
                ),
            )

        if jugador_2:
            jugador_2_ocupado = (
                trabajos_mismo_cambio.filter(
                    Q(jugador_1=jugador_2)
                    | Q(jugador_2=jugador_2)
                ).exists()
            )

            if jugador_2_ocupado:
                self.add_error(
                    "jugador_2",
                    (
                        f"{jugador_2} ya tiene una actividad "
                        f"cargada en el cambio {cambio}."
                    ),
                )

        return cleaned_data


class ObservacionJugadorForm(forms.ModelForm):
    class Meta:
        model = ObservacionJugador

        fields = [
            "texto",
        ]

        labels = {
            "texto": "Observación individual",
        }

        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Ejemplo: mejorar recepción, "
                        "trabajar desplazamiento lateral "
                        "o entrenó con molestias."
                    ),
                    "autocomplete": "off",
                }
            ),
        }

    def clean_texto(self):
        texto = self.cleaned_data.get(
            "texto",
            "",
        ).strip()

        if not texto:
            raise forms.ValidationError(
                "Escribí una observación antes de guardarla."
            )

        if len(texto) < 3:
            raise forms.ValidationError(
                "La observación es demasiado corta."
            )

        return texto


class MotivoAusenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia

        fields = [
            "motivo_ausencia",
            "detalle_ausencia",
        ]

        labels = {
            "motivo_ausencia": "Motivo de ausencia",
            "detalle_ausencia": "Detalle opcional",
        }

        widgets = {
            "motivo_ausencia": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "detalle_ausencia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ejemplo: reposo médico, viaje por "
                        "torneo o examen universitario."
                    ),
                    "autocomplete": "off",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        motivo = cleaned_data.get(
            "motivo_ausencia"
        )

        detalle = cleaned_data.get(
            "detalle_ausencia",
            "",
        ).strip()

        if not motivo:
            self.add_error(
                "motivo_ausencia",
                "Seleccioná el motivo de la ausencia.",
            )

        if (
            motivo == Asistencia.MotivoAusencia.OTRO
            and not detalle
        ):
            self.add_error(
                "detalle_ausencia",
                (
                    "Explicá el motivo cuando "
                    "seleccionás Otro."
                ),
            )

        cleaned_data[
            "detalle_ausencia"
        ] = detalle

        return cleaned_data


class PartidoTurnoForm(forms.ModelForm):
    class Meta:
        model = PartidoTurno

        fields = [
            "jugador_1",
            "jugador_2",
            "detalle",
        ]

        labels = {
            "jugador_1": "Jugador 1",
            "jugador_2": "Jugador 2",
            "detalle": "Detalle opcional",
        }

        widgets = {
            "jugador_1": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "jugador_2": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "detalle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ejemplo: partido final del turno"
                    ),
                }
            ),
        }

    def __init__(
        self,
        *args,
        entrenamiento=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.entrenamiento = entrenamiento

        if not entrenamiento:
            jugadores = Jugador.objects.none()

        else:
            jugadores_ids = (
                entrenamiento
                .asistencias
                .filter(
                    estado__in=[
                        "asistio",
                        "tarde",
                    ]
                )
                .values_list(
                    "jugador_id",
                    flat=True,
                )
            )

            jugadores = Jugador.objects.filter(
                id__in=jugadores_ids,
                activo=True,
            )

            if entrenamiento.club_id:
                jugadores = jugadores.filter(
                    club=entrenamiento.club,
                )

            jugadores = jugadores.order_by(
                "apellido",
                "nombre",
            )

        self.fields[
            "jugador_1"
        ].queryset = jugadores

        self.fields[
            "jugador_2"
        ].queryset = jugadores

    def clean(self):
        cleaned_data = super().clean()

        jugador_1 = cleaned_data.get(
            "jugador_1"
        )

        jugador_2 = cleaned_data.get(
            "jugador_2"
        )

        if (
            jugador_1
            and jugador_2
            and jugador_1 == jugador_2
        ):
            raise forms.ValidationError(
                "Un jugador no puede jugar contra sí mismo."
            )

        if (
            self.entrenamiento
            and self.entrenamiento.club_id
        ):

            if (
                jugador_1
                and jugador_1.club_id
                != self.entrenamiento.club_id
            ):
                self.add_error(
                    "jugador_1",
                    (
                        "El jugador seleccionado no "
                        "pertenece a este club."
                    ),
                )

            if (
                jugador_2
                and jugador_2.club_id
                != self.entrenamiento.club_id
            ):
                self.add_error(
                    "jugador_2",
                    (
                        "El jugador seleccionado no "
                        "pertenece a este club."
                    ),
                )

        return cleaned_data


class SetPartidoForm(forms.ModelForm):
    class Meta:
        model = SetPartido

        fields = [
            "puntos_jugador_1",
            "puntos_jugador_2",
        ]

        labels = {
            "puntos_jugador_1": "Puntos J1",
            "puntos_jugador_2": "Puntos J2",
        }

        widgets = {
            "puntos_jugador_1": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "puntos_jugador_2": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        puntos_1 = cleaned_data.get(
            "puntos_jugador_1"
        )

        puntos_2 = cleaned_data.get(
            "puntos_jugador_2"
        )

        if (
            puntos_1 is None
            or puntos_2 is None
        ):
            return cleaned_data

        if puntos_1 == puntos_2:
            raise forms.ValidationError(
                "Un set no puede terminar empatado."
            )

        ganador = max(
            puntos_1,
            puntos_2,
        )

        perdedor = min(
            puntos_1,
            puntos_2,
        )

        if ganador < 11:
            raise forms.ValidationError(
                (
                    "El ganador del set debe llegar "
                    "al menos a 11 puntos."
                )
            )

        if ganador - perdedor < 2:
            raise forms.ValidationError(
                (
                    "El set debe terminar con una "
                    "diferencia mínima de 2 puntos."
                )
            )

        return cleaned_data


SetPartidoFormSet = inlineformset_factory(
    PartidoTurno,
    SetPartido,
    form=SetPartidoForm,
    extra=5,
    can_delete=True,
    min_num=1,
    validate_min=True,
)