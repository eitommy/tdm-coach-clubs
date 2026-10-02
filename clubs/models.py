import uuid

from django.conf import settings
from django.db import models


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
