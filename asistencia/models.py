from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.db import models
from django.utils import timezone



from clubs.models import Club, TurnoClub





class CategoriaJugador(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="categorias_jugador",
    )

    nombre = models.CharField(
        max_length=100,
    )

    orden = models.PositiveSmallIntegerField(
        default=1,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "orden",
            "nombre",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "club",
                    "nombre",
                ],
                name="categoria_jugador_unica_por_club",
            ),
        ]

        verbose_name = "Categoría de jugador"
        verbose_name_plural = "Categorías de jugadores"

    def __str__(self):
        return self.nombre


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




    categoria = models.ForeignKey(
        CategoriaJugador,
        on_delete=models.PROTECT,
        related_name="jugadores",
        null=True,
        blank=True,
    )

    
    fecha_alta = models.DateField(
        default=timezone.localdate,
        verbose_name="Fecha de alta",
    )

    fecha_baja = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de baja",
    )

    class Meta:

        ordering = [

            "apellido",

            "nombre",

        ]
    def clean(self):
        super().clean()

        if (
            self.club_id
            and self.categoria_id
            and self.categoria.club_id != self.club_id
        ):
            raise ValidationError({
                "categoria": (
                    "La categoría seleccionada pertenece a otro club."
                )
            })




    
        if (
            self.fecha_alta
            and self.fecha_baja
            and self.fecha_baja < self.fecha_alta
        ):
            raise ValidationError({
                "fecha_baja": (
                    "La fecha de baja no puede ser anterior "
                    "a la fecha de alta."
                )
            })


    def __str__(self):

        return f"{self.nombre} {self.apellido}".strip()





class PagoJugador(models.Model):
    class Mes(models.IntegerChoices):
        ENERO = 1, "Enero"
        FEBRERO = 2, "Febrero"
        MARZO = 3, "Marzo"
        ABRIL = 4, "Abril"
        MAYO = 5, "Mayo"
        JUNIO = 6, "Junio"
        JULIO = 7, "Julio"
        AGOSTO = 8, "Agosto"
        SEPTIEMBRE = 9, "Septiembre"
        OCTUBRE = 10, "Octubre"
        NOVIEMBRE = 11, "Noviembre"
        DICIEMBRE = 12, "Diciembre"

    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.CASCADE,
        related_name="pagos",
    )

    anio = models.PositiveSmallIntegerField(
        verbose_name="Año",
    )

    mes = models.PositiveSmallIntegerField(
        choices=Mes.choices,
        verbose_name="Mes",
    )

    pagado = models.BooleanField(
        default=False,
    )

    fecha_pago = models.DateField(
        null=True,
        blank=True,
    )

    observacion = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        ordering = [
            "-anio",
            "-mes",
            "jugador__apellido",
            "jugador__nombre",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "jugador",
                    "anio",
                    "mes",
                ],
                name="pago_jugador_unico_por_mes",
            ),
        ]

        verbose_name = "Estado de cuota"
        verbose_name_plural = "Estados de cuota"

    def __str__(self):
        estado = "Pagado" if self.pagado else "Pendiente"

        return (
            f"{self.jugador} · "
            f"{self.get_mes_display()} {self.anio} · "
            f"{estado}"
        )


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

    Durante la transición conservamos el campo entero \turno\

    para que la aplicación actual siga funcionando.



    El nuevo sistema utilizará \turno_config\, que apunta a TurnoClub.

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



    #* CAMPO VIEJO.*

    #* Se mantiene temporalmente para no romper la app existente.*

    turno = models.PositiveSmallIntegerField(

        choices=TURNOS,

        null=True,

        blank=True,

    )



    #* NUEVO SISTEMA DE TURNOS CONFIGURABLES.*

    turno_config = models.ForeignKey(

        TurnoClub,

        on_delete=models.PROTECT,

        related_name="entrenamientos",

        null=True,

        blank=True,

    )



    #* Campo antiguo relacionado con el User que "tomaba" el turno.*

    #* Lo conservamos durante la migración.*

    entrenador = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="entrenamientos",

    )



    #* Campo usado actualmente por la app para indicar responsable.*

    #* También se conserva temporalmente.*

    entrenador_responsable = models.ForeignKey(

        Entrenador,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="entrenamientos_responsables",

    )



    #* NUEVO SISTEMA.*

    #* El responsable real del turno será un usuario perteneciente al club.*

    #* Conservamos entrenador_responsable temporalmente para no romper*

    #* entrenamientos/datos anteriores durante la migración.*

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



    def clean(self):

        super().clean()



        #* Los registros legacy (club=None) se mantienen sin estas*

        #* validaciones para preservar el histórico existente.*

        if not self.club_id:

            return



        if (

            self.turno_config_id

            and self.turno_config.club_id != self.club_id

        ):

            raise ValidationError({

                "turno_config": (

                    "El turno seleccionado pertenece a otro club."

                )

            })



        if self.responsable_usuario_id:

            perfil = getattr(

                self.responsable_usuario,

                "perfil_club",

                None,

            )



            if (

                perfil is None

                or perfil.club_id != self.club_id

            ):

                raise ValidationError({

                    "responsable_usuario": (

                        "El responsable debe pertenecer al mismo club "

                        "del entrenamiento."

                    )

                })



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



    @property

    def nombre_entrenador(self):

        if self.responsable_usuario:

            return (

                self.responsable_usuario.get_full_name()

                or self.responsable_usuario.username

            )



        if self.entrenador_responsable:

            return str(self.entrenador_responsable)



        if self.entrenador:

            return (

                self.entrenador.get_full_name()

                or self.entrenador.username

            )



        return "Sin entrenador"



    def __str__(self):

        estado = (

            "Finalizado"

            if self.finalizado

            else "Abierto"

        )



        return (

            f"{self.fecha} - "

            f"{self.nombre_turno} - "

            f"{self.nombre_entrenador} - "

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



    def clean(self):

        super().clean()



        if (

            self.entrenamiento_id

            and self.entrenamiento.club_id

            and self.jugador_id

            and self.jugador.club_id != self.entrenamiento.club_id

        ):

            raise ValidationError({

                "jugador": (

                    "El jugador debe pertenecer al mismo club "

                    "del entrenamiento."

                )

            })



    def __str__(self):

        return (

            f"{self.jugador} - "

            f"{self.entrenamiento.fecha} - "

            f"{self.entrenamiento}"

        )





class CategoriaEjercicio(models.Model):

    club = models.ForeignKey(

        Club,

        on_delete=models.CASCADE,

        related_name="categorias_ejercicio",

    )



    nombre = models.CharField(

        max_length=100,

    )



    orden = models.PositiveSmallIntegerField(

        default=1,

    )



    activo = models.BooleanField(

        default=True,

    )



    class Meta:

        ordering = [

            "orden",

            "nombre",

        ]



        constraints = [

            models.UniqueConstraint(

                fields=[

                    "club",

                    "nombre",

                ],

                name="categoria_ejercicio_unica_por_club",

            ),

        ]



        verbose_name = "Categoría de ejercicio"

        verbose_name_plural = "Categorías de ejercicios"



    def __str__(self):

        return self.nombre





class Ejercicio(models.Model):

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



    categoria_config = models.ForeignKey(

        CategoriaEjercicio,

        on_delete=models.PROTECT,

        related_name="ejercicios",

        null=True,

        blank=True,

        help_text="Categoría configurable del club.",

    )



    activo = models.BooleanField(

        default=True,

    )



    class Meta:

        ordering = [

            "categoria_config__orden",

            "categoria_config__nombre",

            "nombre",

        ]



        constraints = [

            models.UniqueConstraint(

                fields=[

                    "club",

                    "nombre",

                    "categoria_config",

                ],

                name="ejercicio_unico_por_club_categoria_config",

            ),

            models.CheckConstraint(

                condition=(

                    models.Q(club__isnull=True)

                    | models.Q(categoria_config__isnull=False)

                ),

                name="ejercicio_comercial_requiere_categoria_config",

            ),

        ]



    def clean(self):

        super().clean()



        #* Los ejercicios legacy pueden seguir sin club/categoría.*

        if not self.club_id:

            return



        if (

            self.categoria_config_id

            and self.categoria_config.club_id != self.club_id

        ):

            raise ValidationError({

                "categoria_config": (

                    "La categoría seleccionada pertenece a otro club."

                )

            })



    @property

    def nombre_categoria(self):

        if self.categoria_config_id:

            return self.categoria_config.nombre



        return "Sin categoría"



    def __str__(self):

        return (

            f"{self.nombre_categoria} - "

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

            "ejercicio__categoria_config__orden",

            "ejercicio__categoria_config__nombre",

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

        super().clean()



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



        if (

            self.entrenamiento_id

            and self.entrenamiento.club_id

        ):

            club_id = self.entrenamiento.club_id



            if (

                self.jugador_1_id

                and self.jugador_1.club_id != club_id

            ):

                raise ValidationError({

                    "jugador_1": (

                        "El jugador debe pertenecer al mismo club "

                        "del entrenamiento."

                    )

                })



            if (

                self.jugador_2_id

                and self.jugador_2.club_id != club_id

            ):

                raise ValidationError({

                    "jugador_2": (

                        "El compañero debe pertenecer al mismo club "

                        "del entrenamiento."

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

            "ejercicio__categoria_config__orden",

            "ejercicio__categoria_config__nombre",

            "ejercicio__nombre",

        ]



        verbose_name = "Ejercicio del turno"

        verbose_name_plural = "Ejercicios del turno"



    def clean(self):

        super().clean()



        if (

            self.entrenamiento_id

            and self.entrenamiento.club_id

            and self.ejercicio_id

            and self.ejercicio.club_id != self.entrenamiento.club_id

        ):

            raise ValidationError({

                "ejercicio": (

                    "El ejercicio debe pertenecer al mismo club "

                    "del entrenamiento."

                )

            })



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



    def clean(self):

        super().clean()



        if (

            self.entrenamiento_id

            and self.entrenamiento.club_id

            and self.jugador_id

            and self.jugador.club_id != self.entrenamiento.club_id

        ):

            raise ValidationError({

                "jugador": (

                    "El jugador debe pertenecer al mismo club "

                    "del entrenamiento."

                )

            })



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



    def clean(self):

        super().clean()



        if not (

            self.entrenamiento_id

            and self.entrenamiento.club_id

        ):

            return



        club_id = self.entrenamiento.club_id



        if (

            self.jugador_1_id

            and self.jugador_1.club_id != club_id

        ):

            raise ValidationError({

                "jugador_1": (

                    "El jugador 1 debe pertenecer al mismo club "

                    "del entrenamiento."

                )

            })



        if (

            self.jugador_2_id

            and self.jugador_2.club_id != club_id

        ):

            raise ValidationError({

                "jugador_2": (

                    "El jugador 2 debe pertenecer al mismo club "

                    "del entrenamiento."

                )

            })



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