from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "asistencia",
            "0019_categoria_ejercicio_configurable",
        ),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="ejercicio",
            name="ejercicio_unico_por_club_categoria",
        ),
        migrations.AlterModelOptions(
            name="ejercicio",
            options={
                "ordering": [
                    "categoria_config__orden",
                    "categoria_config__nombre",
                    "nombre",
                ],
            },
        ),
        migrations.AlterModelOptions(
            name="ejerciciorealizado",
            options={
                "ordering": [
                    "-fecha",
                    "jugador__apellido",
                    "ejercicio__categoria_config__orden",
                    "ejercicio__categoria_config__nombre",
                    "ejercicio__nombre",
                ],
            },
        ),
        migrations.AlterModelOptions(
            name="ejercicioturno",
            options={
                "ordering": [
                    "entrenamiento__fecha",
                    "entrenamiento__turno_config__orden",
                    "ejercicio__categoria_config__orden",
                    "ejercicio__categoria_config__nombre",
                    "ejercicio__nombre",
                ],
                "verbose_name": "Ejercicio del turno",
                "verbose_name_plural": "Ejercicios del turno",
            },
        ),
        migrations.RemoveField(
            model_name="ejercicio",
            name="categoria",
        ),
        migrations.AddConstraint(
            model_name="ejercicio",
            constraint=models.UniqueConstraint(
                fields=(
                    "club",
                    "nombre",
                    "categoria_config",
                ),
                name="ejercicio_unico_por_club_categoria_config",
            ),
        ),
    ]
