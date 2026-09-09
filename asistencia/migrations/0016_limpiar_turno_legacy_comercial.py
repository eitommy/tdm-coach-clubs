from django.db import migrations


def limpiar_turno_legacy_comercial(apps, schema_editor):
    Entrenamiento = apps.get_model(
        "asistencia",
        "Entrenamiento",
    )

    (
        Entrenamiento.objects
        .filter(
            club__isnull=False,
            turno_config__isnull=False,
        )
        .update(turno=None)
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "asistencia",
            "0015_alter_ejercicioturno_options_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            limpiar_turno_legacy_comercial,
            migrations.RunPython.noop,
        ),
    ]
