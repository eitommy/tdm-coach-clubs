from django.db import migrations, models
import django.db.models.deletion


CATEGORIAS_LEGACY = {
    "movilidad": ("Movilidad", 1),
    "reaccion": ("Reacción", 2),
    "saque": ("Saque", 3),
    "recepcion": ("Recepción", 4),
}


def crear_categorias_y_vincular_ejercicios(apps, schema_editor):
    CategoriaEjercicio = apps.get_model(
        "asistencia",
        "CategoriaEjercicio",
    )
    Ejercicio = apps.get_model(
        "asistencia",
        "Ejercicio",
    )

    ejercicios = (
        Ejercicio.objects
        .filter(club__isnull=False)
        .order_by("club_id", "id")
    )

    cache = {}

    for ejercicio in ejercicios.iterator():
        codigo = ejercicio.categoria or "movilidad"
        nombre, orden = CATEGORIAS_LEGACY.get(
            codigo,
            (
                codigo.replace("_", " ").strip().title()
                or "Sin categoría",
                99,
            ),
        )

        clave = (ejercicio.club_id, nombre.casefold())
        categoria = cache.get(clave)

        if categoria is None:
            categoria, _ = CategoriaEjercicio.objects.get_or_create(
                club_id=ejercicio.club_id,
                nombre=nombre,
                defaults={
                    "orden": orden,
                    "activo": True,
                },
            )
            cache[clave] = categoria

        ejercicio.categoria_config_id = categoria.id
        ejercicio.save(
            update_fields=["categoria_config"],
        )


def desvincular_categorias(apps, schema_editor):
    Ejercicio = apps.get_model(
        "asistencia",
        "Ejercicio",
    )

    Ejercicio.objects.update(
        categoria_config=None,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("asistencia", "0018_entrenamiento_entrenamiento_comercial_sin_entrenador_legacy"),
        ("clubs", "0003_turnoclub_turno_unico_por_club_dia_orden"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategoriaEjercicio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nombre",
                    models.CharField(max_length=100),
                ),
                (
                    "orden",
                    models.PositiveSmallIntegerField(default=1),
                ),
                (
                    "activo",
                    models.BooleanField(default=True),
                ),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="categorias_ejercicio",
                        to="clubs.club",
                    ),
                ),
            ],
            options={
                "verbose_name": "Categoría de ejercicio",
                "verbose_name_plural": "Categorías de ejercicios",
                "ordering": ["orden", "nombre"],
            },
        ),
        migrations.AddConstraint(
            model_name="categoriaejercicio",
            constraint=models.UniqueConstraint(
                fields=("club", "nombre"),
                name="categoria_ejercicio_unica_por_club",
            ),
        ),
        migrations.AddField(
            model_name="ejercicio",
            name="categoria_config",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Categoría configurable del club. "
                    "El campo categoria se conserva temporalmente por compatibilidad."
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ejercicios",
                to="asistencia.categoriaejercicio",
            ),
        ),
        migrations.RunPython(
            crear_categorias_y_vincular_ejercicios,
            desvincular_categorias,
        ),
    ]
