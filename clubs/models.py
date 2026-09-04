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