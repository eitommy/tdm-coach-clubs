from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "asistencia",
            "0020_eliminar_categoria_legacy_ejercicio",
        ),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="ejercicio",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(club__isnull=True)
                    | models.Q(categoria_config__isnull=False)
                ),
                name="ejercicio_comercial_requiere_categoria_config",
            ),
        ),
    ]
