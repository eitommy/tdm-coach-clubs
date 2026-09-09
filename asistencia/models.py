from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from clubs.models import Club, TurnoClub


class Jugador(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="jugadores",
        null=True,
        blank=True,
    )

    nombre = models.CharField(
        max_length=100,
    )

    apellido = models.CharField(
        max_length=100,
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "apellido",
            "nombre",
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()


class Entrenador(models.Model):
    """
    MODELO TEMPORAL.

    Lo conservamos durante la migración porque la app actual todavía
    utiliza entrenador_responsable en Entrenamiento.

    Más adelante evaluaremos reemplazarlo por User + PerfilUsuario.
    """

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="entrenadores_legacy",
        null=True,
        blank=True,
    )

    nombre = models.CharField(
        max_length=100,
    )

    apellido = models.CharField(
        max_length=100,
        blank=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "apellido",
            "nombre",
        ]

        verbose_name = "Entrenador"
        verbose_name_plural = "Entrenadores"

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()


class Entrenamiento(models.Model):
    """
    Durante la transición conservamos el campo entero `turno`
    para que la aplicación actual siga funcionando.

    El nuevo sistema utilizará `turno_config`, que apunta a TurnoClub.
    Cuando todas las vistas hayan sido migradas, eliminaremos
    definitivamente TURNOS y el campo turno.
    """

    TURNOS = [
        (1, "Turno 1"),
        (2, "Turno 2"),
        (3, "Turno 3"),
    ]

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="entrenamientos",
        null=True,
        blank=True,
    )

    fecha = models.DateField()

    # CAMPO VIEJO.
    # Se mantiene temporalmente para no romper la app existente.
    turno = models.PositiveSmallIntegerField(
        choices=TURNOS,
        null=True,
        blank=True,
    )

    # NUEVO SISTEMA DE TURNOS CONFIGURABLES.
    turno_config = models.ForeignKey(
        TurnoClub,
        on_delete=models.PROTECT,
        related_name="entrenamientos",
        null=True,
        blank=True,
    )

    # Campo antiguo relacionado con el User que "tomaba" el turno.
    # Lo conservamos durante la migración.
    entrenador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entrenamientos",
    )

    # Campo usado actualmente por la app para indicar responsable.
    # También se conserva temporalmente.
    entrenador_responsable = models.ForeignKey(
        Entrenador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entrenamientos_responsables",
    )

    # NUEVO SISTEMA.
    # El responsable real del turno será un usuario perteneciente al club.
    # Conservamos entrenador_responsable temporalmente para no romper
    # entrenamientos/datos anteriores durante la migración.
    responsable_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="turnos_como_responsable",
    )

    observaciones = models.TextField(
        blank=True,
    )

    class MotivoNoEntrenamiento(models.TextChoices):
        FERIADO = "feriado", "Feriado"
        TORNEO = "torneo", "Torneo"
        CLUB_CERRADO = "club_cerrado", "Club cerrado"
        VIAJE = "viaje", "Viaje"
        SUSPENDIDO = "suspendido", "Suspendido"
        OTRO = "otro", "Otro"

    no_se_entreno = models.BooleanField(
        default=False,
    )

    motivo_no_entrenamiento = models.CharField(
        max_length=30,
        choices=MotivoNoEntrenamiento.choices,
        blank=True,
        default="",
    )

    detalle_no_entrenamiento = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    finalizado = models.BooleanField(
        default=False,
    )

    finalizado_el = models.DateTimeField(
        null=True,
        blank=True,
    )

    finalizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entrenamientos_finalizados",
    )

    class Meta:
        ordering = [
            "-fecha",
            "turno_config__orden",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "club",
                    "fecha",
                    "turno_config",
                ],
                name="entrenamiento_unico_club_fecha_turno_config",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(club__isnull=True)
                    | models.Q(turno_config__isnull=False)
                ),
                name="entrenamiento_comercial_requiere_turno_config",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(club__isnull=True)
                    | models.Q(turno__isnull=True)
                ),
                name="entrenamiento_comercial_sin_turno_legacy",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(club__isnull=True)
                    | (
                        models.Q(entrenador__isnull=True)
                        & models.Q(entrenador_responsable__isnull=True)
                    )
                ),
                name="entrenamiento_comercial_sin_entrenador_legacy",
            ),
        ]

    @property
    def nombre_turno(self):
        if self.turno_config:
            return self.turno_config.nombre

        if self.turno:
            return f"Turno {self.turno}"

        return "Sin turno"

    @property
    def horario_turno(self):
        if not self.turno_config:
            return ""

        inicio = self.turno_config.hora_inicio
        fin = self.turno_config.hora_fin

        if inicio and fin:
            return (
                f"{inicio.strftime('%H:%M')}-"
                f"{fin.strftime('%H:%M')}"
            )

        if inicio:
            return inicio.strftime("%H:%M")

        if fin:
            return fin.strftime("%H:%M")

        return ""

    @property
    def nombre_turno_completo(self):
        if self.horario_turno:
            return f"{self.nombre_turno} · {self.horario_turno}"

        return self.nombre_turno

    def __str__(self):
        if self.responsable_usuario:
            nombre_entrenador = (
                self.responsable_usuario.get_full_name()
                or self.responsable_usuario.username
            )

        elif self.entrenador_responsable:
            nombre_entrenador = str(
                self.entrenador_responsable
            )

        elif self.entrenador:
            nombre_entrenador = (
                self.entrenador.get_full_name()
                or self.entrenador.username
            )

        else:
            nombre_entrenador = "Sin entrenador"

        nombre_turno = self.nombre_turno

        estado = (
            "Finalizado"
            if self.finalizado
            else "Abierto"
        )

        return (
            f"{self.fecha} - "
            f"{nombre_turno} - "
            f"{nombre_entrenador} - "
            f"{estado}"
        )


class Asistencia(models.Model):
    class MotivoAusencia(models.TextChoices):
        ENFERMEDAD = "enfermedad", "Enfermedad"
        VIAJE = "viaje", "Viaje"
        COMPETENCIA = "competencia", "Competencia"
        ESTUDIO = "estudio", "Estudio"
        SIN_AVISO = "sin_aviso", "Sin aviso"
        OTRO = "otro", "Otro"

    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name="asistencias",
    )

    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="asistencias",
    )

    estado = models.CharField(
        max_length=20,
        choices=[
            ("pendiente", "Pendiente"),
            ("asistio", "Asistió"),
            ("ausente", "Ausente"),
            ("tarde", "Tarde"),
        ],
        default="pendiente",
    )

    motivo_ausencia = models.CharField(
        max_length=20,
        choices=MotivoAusencia.choices,
        blank=True,
        default="",
    )

    detalle_ausencia = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        unique_together = (
            "entrenamiento",
            "jugador",
        )

    def __str__(self):
        return (
            f"{self.jugador} - "
            f"{self.entrenamiento.fecha} - "
            f"{self.entrenamiento}"
        )


class Ejercicio(models.Model):
    class Categoria(models.TextChoices):
        MOVILIDAD = "movilidad", "Movilidad"
        REACCION = "reaccion", "Reacción"
        SAQUE = "saque", "Saque"
        RECEPCION = "recepcion", "Recepción"

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="ejercicios",
        null=True,
        blank=True,
    )

    nombre = models.CharField(
        max_length=150,
    )

    # Por ahora mantenemos las categorías actuales.
    # Después las haremos configurables por club.
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.MOVILIDAD,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "categoria",
            "nombre",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "club",
                    "nombre",
                    "categoria",
                ],
                name="ejercicio_unico_por_club_categoria",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_categoria_display()} - "
            f"{self.nombre}"
        )


class EjercicioRealizado(models.Model):
    """
    Modelo legado.

    Por ahora NO lo eliminamos.
    Una vez que terminemos la migración confirmamos si ya no existe
    ninguna dependencia y recién ahí lo borramos.
    """

    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="ejercicios_realizados",
    )

    fecha = models.DateField()

    ejercicio = models.ForeignKey(
        Ejercicio,
        on_delete=models.CASCADE,
        related_name="realizaciones",
    )

    class Meta:
        unique_together = (
            "jugador",
            "fecha",
            "ejercicio",
        )

        ordering = [
            "-fecha",
            "jugador__apellido",
            "ejercicio__categoria",
            "ejercicio__nombre",
        ]

    def __str__(self):
        return (
            f"{self.jugador} - "
            f"{self.fecha} - "
            f"{self.ejercicio}"
        )


class TrabajoTurno(models.Model):
    class Tipo(models.TextChoices):
        PAREJA = "pareja", "Pareja"
        MULTIPELOTA = "multipelota", "Multipelota"
        ENTRENADOR = "entrenador", "Con entrenador"
        LIBRE = "libre", "Libre / descanso"
        OTRO = "otro", "Otro"

    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name="trabajos",
    )

    cambio = models.PositiveIntegerField(
        verbose_name="Número de cambio",
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.PAREJA,
    )

    jugador_1 = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="trabajos_principales",
        verbose_name="Jugador",
    )

    jugador_2 = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="trabajos_secundarios",
        verbose_name="Compañero",
        null=True,
        blank=True,
    )

    detalle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Detalle",
        help_text=(
            "Ejemplo: recepción, saque y tercera pelota, "
            "trabajo físico, etc."
        ),
    )

    class Meta:
        ordering = [
            "cambio",
            "id",
        ]

        verbose_name = "Trabajo del turno"
        verbose_name_plural = "Trabajos del turno"

    def clean(self):
        if self.tipo == self.Tipo.PAREJA:
            if not self.jugador_2:
                raise ValidationError({
                    "jugador_2": (
                        "Para una pareja tenés que seleccionar "
                        "dos jugadores."
                    )
                })

            if self.jugador_1_id == self.jugador_2_id:
                raise ValidationError({
                    "jugador_2": (
                        "Un jugador no puede formar pareja consigo mismo."
                    )
                })

        elif self.jugador_2:
            raise ValidationError({
                "jugador_2": (
                    "El segundo jugador solo se usa cuando "
                    "el tipo es Pareja."
                )
            })

    def __str__(self):
        if (
            self.tipo == self.Tipo.PAREJA
            and self.jugador_2
        ):
            trabajo = (
                f"{self.jugador_1} - "
                f"{self.jugador_2}"
            )

        else:
            trabajo = (
                f"{self.jugador_1} · "
                f"{self.get_tipo_display()}"
            )

        return (
            f"{self.entrenamiento.fecha} · "
            f"{self.entrenamiento} · "
            f"Cambio {self.cambio}: "
            f"{trabajo}"
        )


class EjercicioTurno(models.Model):
    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name="ejercicios_turno",
    )

    ejercicio = models.ForeignKey(
        Ejercicio,
        on_delete=models.CASCADE,
        related_name="turnos_realizados",
    )

    creado_el = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = (
            "entrenamiento",
            "ejercicio",
        )

        ordering = [
            "entrenamiento__fecha",
            "entrenamiento__turno_config__orden",
            "ejercicio__categoria",
            "ejercicio__nombre",
        ]

        verbose_name = "Ejercicio del turno"
        verbose_name_plural = "Ejercicios del turno"

    def __str__(self):
        return (
            f"{self.entrenamiento.fecha} - "
            f"{self.entrenamiento} - "
            f"{self.ejercicio}"
        )


class ObservacionJugador(models.Model):
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="observaciones",
    )

    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name="observaciones_jugadores",
    )

    texto = models.TextField(
        verbose_name="Observación",
    )

    creada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="observaciones_creadas",
    )

    creada_el = models.DateTimeField(
        auto_now_add=True,
    )

    actualizada_el = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-creada_el",
        ]

        verbose_name = "Observación de jugador"
        verbose_name_plural = "Observaciones de jugadores"

    def __str__(self):
        return (
            f"{self.jugador} · "
            f"{self.entrenamiento.fecha} · "
            f"{self.entrenamiento}"
        )


class PartidoTurno(models.Model):
    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name="partidos",
    )

    jugador_1 = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="partidos_como_jugador_1",
    )

    jugador_2 = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="partidos_como_jugador_2",
    )

    detalle = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Ejemplo: partido final del turno "
            "o partido de entrenamiento."
        ),
    )

    creado_el = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "id",
        ]

        verbose_name = "Partido del turno"
        verbose_name_plural = "Partidos del turno"

    def __str__(self):
        return (
            f"{self.jugador_1} vs "
            f"{self.jugador_2} · "
            f"{self.entrenamiento.fecha} · "
            f"{self.entrenamiento}"
        )

    @property
    def sets_jugador_1(self):
        return self.sets.filter(
            puntos_jugador_1__gt=models.F(
                "puntos_jugador_2"
            )
        ).count()

    @property
    def sets_jugador_2(self):
        return self.sets.filter(
            puntos_jugador_2__gt=models.F(
                "puntos_jugador_1"
            )
        ).count()

    @property
    def resultado_general(self):
        return (
            f"{self.sets_jugador_1}-"
            f"{self.sets_jugador_2}"
        )

    @property
    def ganador(self):
        if self.sets_jugador_1 > self.sets_jugador_2:
            return self.jugador_1

        if self.sets_jugador_2 > self.sets_jugador_1:
            return self.jugador_2

        return None


class SetPartido(models.Model):
    partido = models.ForeignKey(
        PartidoTurno,
        on_delete=models.CASCADE,
        related_name="sets",
    )

    numero = models.PositiveIntegerField()

    puntos_jugador_1 = models.PositiveIntegerField()

    puntos_jugador_2 = models.PositiveIntegerField()

    class Meta:
        ordering = [
            "numero",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "partido",
                    "numero",
                ],
                name="set_unico_por_partido",
            ),
        ]

        verbose_name = "Set del partido"
        verbose_name_plural = "Sets del partido"

    def __str__(self):
        return (
            f"Set {self.numero}: "
            f"{self.puntos_jugador_1}-"
            f"{self.puntos_jugador_2}"
        )