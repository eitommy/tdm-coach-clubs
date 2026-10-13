import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Club(models.Model):
    class EstadoPago(models.TextChoices):
        AL_DIA = "al_dia", "Al día"
        PENDIENTE = "pendiente", "Pago pendiente"
        VENCIDO = "vencido", "Vencido"

    nombre = models.CharField(max_length=150)

    logo = models.ImageField(
        upload_to="clubes/logos/",
        blank=True,
        null=True,
    )

    color_primario = models.CharField(
        max_length=7,
        default="#2563EB",
    )

    color_secundario = models.CharField(
        max_length=7,
        default="#111827",
    )

    email = models.EmailField(blank=True)

    telefono = models.CharField(
        max_length=50,
        blank=True,
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    estado_pago = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
        help_text=(
            "Estado informativo de la suscripción. "
            "No bloquea automáticamente el acceso al club."
        ),
    )

    pagado_hasta = models.DateField(
        null=True,
        blank=True,
        help_text="Última fecha cubierta por el pago del club.",
    )

    observacion_pago = models.TextField(
        blank=True,
        help_text=(
            "Nota interna visible para el administrador técnico."
        ),
    )

    creado = models.DateTimeField(auto_now_add=True)

    @property
    def estado_pago_actual(self):
        """
        Devuelve el estado real de la suscripción
        utilizando la fecha actual.

        Esto evita que un club quede mostrando "Al día"
        después de que su suscripción haya vencido.
        """

        if not self.pagado_hasta:
            return self.EstadoPago.PENDIENTE

        if self.pagado_hasta >= timezone.localdate():
            return self.EstadoPago.AL_DIA

        return self.EstadoPago.VENCIDO

    def get_estado_pago_actual_display(self):
        """
        Devuelve el texto visible del estado calculado.
        """

        return dict(self.EstadoPago.choices).get(
            self.estado_pago_actual,
            self.estado_pago_actual,
        )

    def actualizar_estado_pago(self):
        """
        Sincroniza los campos guardados estado_pago
        y pagado_hasta utilizando los pagos registrados.
        """

        ultimo_pago = (
            self.pagos_suscripcion
            .order_by(
                "-periodo_hasta",
                "-fecha_pago",
                "-id",
            )
            .first()
        )

        if ultimo_pago is None:
            nuevo_pagado_hasta = None
            nuevo_estado = self.EstadoPago.PENDIENTE

        else:
            nuevo_pagado_hasta = ultimo_pago.periodo_hasta

            if nuevo_pagado_hasta >= timezone.localdate():
                nuevo_estado = self.EstadoPago.AL_DIA
            else:
                nuevo_estado = self.EstadoPago.VENCIDO

        Club.objects.filter(
            pk=self.pk
        ).update(
            pagado_hasta=nuevo_pagado_hasta,
            estado_pago=nuevo_estado,
        )

        self.pagado_hasta = nuevo_pagado_hasta
        self.estado_pago = nuevo_estado

    def __str__(self):
        return self.nombre


class InvitacionClub(models.Model):
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    referencia = models.CharField(
        max_length=150,
        blank=True,
        help_text=(
            "Nombre interno opcional para identificar a quién se envió "
            "la invitación. Ej: Spin TDM."
        ),
    )

    creada = models.DateTimeField(auto_now_add=True)

    usada_en = models.DateTimeField(
        null=True,
        blank=True,
    )

    club_creado = models.OneToOneField(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitacion_origen",
    )

    @property
    def usada(self):
        return self.usada_en is not None

    def __str__(self):
        estado = "Usada" if self.usada else "Disponible"
        referencia = self.referencia or str(self.token)

        return f"{referencia} - {estado}"


class PerfilUsuario(models.Model):
    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        ENTRENADOR = "entrenador", "Entrenador"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_club",
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="usuarios",
    )

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ENTRENADOR,
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.club.nombre}"


class TurnoClub(models.Model):
    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="turnos",
    )

    dia_semana = models.PositiveSmallIntegerField(
        choices=DiaSemana.choices,
    )

    nombre = models.CharField(
        max_length=100,
    )

    hora_inicio = models.TimeField(
        null=True,
        blank=True,
    )

    hora_fin = models.TimeField(
        null=True,
        blank=True,
    )

    orden = models.PositiveSmallIntegerField(
        default=1,
    )

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = [
            "dia_semana",
            "orden",
            "hora_inicio",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "club",
                    "dia_semana",
                    "orden",
                ],
                name="turno_unico_por_club_dia_orden",
            ),
        ]

    def __str__(self):
        return (
            f"{self.club.nombre} - "
            f"{self.get_dia_semana_display()} - "
            f"{self.nombre}"
        )


class PagoClub(models.Model):
    class MetodoPago(models.TextChoices):
        TRANSFERENCIA = "transferencia", "Transferencia"
        EFECTIVO = "efectivo", "Efectivo"
        MERCADO_PAGO = "mercado_pago", "Mercado Pago"
        OTRO = "otro", "Otro"

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="pagos_suscripcion",
    )

    fecha_pago = models.DateField(
        default=timezone.localdate,
    )

    periodo_desde = models.DateField()

    periodo_hasta = models.DateField()

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    metodo_pago = models.CharField(
        max_length=30,
        choices=MetodoPago.choices,
        default=MetodoPago.TRANSFERENCIA,
    )

    referencia = models.CharField(
        max_length=150,
        blank=True,
    )

    observacion = models.TextField(
        blank=True,
    )

    creado = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-fecha_pago",
            "-id",
        ]

    def clean(self):
        super().clean()

        if (
            self.periodo_desde
            and self.periodo_hasta
            and self.periodo_hasta < self.periodo_desde
        ):
            raise ValidationError(
                {
                    "periodo_hasta": (
                        "La fecha hasta no puede ser anterior "
                        "a la fecha desde."
                    )
                }
            )

    def save(self, *args, **kwargs):
        club_anterior_id = None

        if self.pk:
            club_anterior_id = (
                PagoClub.objects
                .filter(pk=self.pk)
                .values_list(
                    "club_id",
                    flat=True,
                )
                .first()
            )

        super().save(*args, **kwargs)

        self.club.actualizar_estado_pago()

        if (
            club_anterior_id
            and club_anterior_id != self.club_id
        ):
            club_anterior = (
                Club.objects
                .filter(pk=club_anterior_id)
                .first()
            )

            if club_anterior:
                club_anterior.actualizar_estado_pago()

    def delete(self, *args, **kwargs):
        club = self.club

        resultado = super().delete(
            *args,
            **kwargs,
        )

        club.actualizar_estado_pago()

        return resultado

    def __str__(self):
        return (
            f"{self.club.nombre} - "
            f"{self.periodo_desde:%d/%m/%Y} "
            f"al "
            f"{self.periodo_hasta:%d/%m/%Y}"
        )