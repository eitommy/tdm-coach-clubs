from django.conf import settings
from django.db import models


class Club(models.Model):
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

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


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
