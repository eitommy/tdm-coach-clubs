import django.utils.timezone

from django.db import migrations, models


def completar_historial_jugadores(apps, schema_editor):
    Jugador = apps.get_model(
        "asistencia",
        "Jugador",
    )

    Asistencia = apps.get_model(
        "asistencia",
        "Asistencia",
    )

    hoy = django.utils.timezone.localdate()

    for jugador in Jugador.objects.all().iterator():
        primera_asistencia = (
            Asistencia.objects
            .filter(
                jugador_id=jugador.id,
            )
            .order_by(
                "entrenamiento__fecha",
                "id",
            )
            .values_list(
                "entrenamiento__fecha",
                flat=True,
            )
            .first()
        )

        cambios = {}

        if primera_asistencia:
            cambios["fecha_alta"] = primera_asistencia

        if (
            not jugador.activo
            and jugador.fecha_baja is None
        ):
            cambios["fecha_baja"] = hoy

        if cambios:
            Jugador.objects.filter(
                pk=jugador.pk,
            ).update(
                **cambios
            )


def revertir_historial_jugadores(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "asistencia",
            "0023_categoriajugador_jugador_categoria_pagojugador_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="jugador",
            name="fecha_alta",
            field=models.DateField(
                default=django.utils.timezone.localdate,
                verbose_name="Fecha de alta",
            ),
        ),
        migrations.AddField(
            model_name="jugador",
            name="fecha_baja",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Fecha de baja",
            ),
        ),
        migrations.RunPython(
            completar_historial_jugadores,
            revertir_historial_jugadores,
        ),
    ]
