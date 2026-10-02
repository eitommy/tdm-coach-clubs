from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    ClubForm,
    EditarUsuarioClubForm,
    RegistroClubInvitacionForm,
    TurnoClubForm,
    UsuarioClubForm,
)
from .models import Club, InvitacionClub, PerfilUsuario, TurnoClub
from .utils import (
    obtener_club_usuario,
    requerir_admin_club,
    requerir_club,
)


def _es_ultimo_admin_activo(perfil):
    """
    Devuelve True si el perfil indicado es el último administrador activo
    del club.
    """
    if (
        perfil.rol != PerfilUsuario.Rol.ADMIN
        or not perfil.activo
    ):
        return False

    return not (
        PerfilUsuario.objects
        .filter(
            club=perfil.club,
            rol=PerfilUsuario.Rol.ADMIN,
            activo=True,
            usuario__is_active=True,
        )
        .exclude(pk=perfil.pk)
        .exists()
    )


@requerir_admin_club
def configuracion_club(request):
    club = obtener_club_usuario(request.user)

    if request.method == "POST":
        form = ClubForm(
            request.POST,
            request.FILES,
            instance=club,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La configuración del club se guardó correctamente.",
            )

            return redirect("configuracion_club")

    else:
        form = ClubForm(
            instance=club,
        )

    return render(
        request,
        "clubs/configuracion.html",
        {
            "form": form,
            "club": club,
        },
    )


@requerir_club
def lista_turnos(request):
    club = obtener_club_usuario(request.user)

    turnos = (
        TurnoClub.objects
        .filter(club=club)
        .order_by(
            "dia_semana",
            "orden",
            "hora_inicio",
        )
    )

    return render(
        request,
        "clubs/turnos/lista.html",
        {
            "club": club,
            "turnos": turnos,
        },
    )


@requerir_club
def crear_turno(request):
    club = obtener_club_usuario(request.user)

    if request.method == "POST":
        form = TurnoClubForm(
            request.POST,
            club=club,
        )

        if form.is_valid():
            turno = form.save(commit=False)
            turno.club = club
            turno.save()

            messages.success(
                request,
                "El turno se creó correctamente.",
            )

            return redirect("lista_turnos")

    else:
        form = TurnoClubForm(
            club=club,
        )

    return render(
        request,
        "clubs/turnos/formulario.html",
        {
            "form": form,
            "club": club,
            "titulo": "Nuevo turno",
        },
    )


@requerir_club
def editar_turno(request, turno_id):
    club = obtener_club_usuario(request.user)

    turno = get_object_or_404(
        TurnoClub,
        id=turno_id,
        club=club,
    )

    if request.method == "POST":
        form = TurnoClubForm(
            request.POST,
            instance=turno,
            club=club,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "El turno se actualizó correctamente.",
            )

            return redirect("lista_turnos")

    else:
        form = TurnoClubForm(
            instance=turno,
            club=club,
        )

    return render(
        request,
        "clubs/turnos/formulario.html",
        {
            "form": form,
            "club": club,
            "turno": turno,
            "titulo": "Editar turno",
        },
    )


@requerir_club
def eliminar_turno(request, turno_id):
    club = obtener_club_usuario(request.user)

    turno = get_object_or_404(
        TurnoClub,
        id=turno_id,
        club=club,
    )

    if request.method == "POST":
        nombre_turno = turno.nombre

        try:
            turno.delete()
        except ProtectedError:
            messages.error(
                request,
                (
                    f'El turno "{nombre_turno}" ya tiene entrenamientos '
                    "asociados y no se puede eliminar. "
                    "Podés editarlo y desmarcar «Activo» para dejar de usarlo."
                ),
            )
        else:
            messages.success(
                request,
                (
                    f'El turno "{nombre_turno}" '
                    "se eliminó correctamente."
                ),
            )

        return redirect("lista_turnos")

    return render(
        request,
        "clubs/turnos/eliminar.html",
        {
            "club": club,
            "turno": turno,
        },
    )


@requerir_admin_club
def lista_usuarios(request):
    club = obtener_club_usuario(request.user)

    perfiles = (
        PerfilUsuario.objects
        .filter(club=club)
        .select_related("usuario")
        .order_by(
            "usuario__first_name",
            "usuario__last_name",
            "usuario__username",
        )
    )

    return render(
        request,
        "clubs/usuarios/lista.html",
        {
            "club": club,
            "perfiles": perfiles,
        },
    )


@requerir_admin_club
def crear_usuario(request):
    club = obtener_club_usuario(request.user)

    if request.method == "POST":
        form = UsuarioClubForm(
            request.POST,
        )

        if form.is_valid():
            with transaction.atomic():
                usuario = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    first_name=form.cleaned_data["nombre"],
                    last_name=form.cleaned_data["apellido"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                )

                PerfilUsuario.objects.create(
                    usuario=usuario,
                    club=club,
                    rol=form.cleaned_data["rol"],
                    activo=True,
                )

            messages.success(
                request,
                (
                    f'El usuario "{usuario.username}" '
                    "se creó correctamente."
                ),
            )

            return redirect("lista_usuarios")

    else:
        form = UsuarioClubForm()

    return render(
        request,
        "clubs/usuarios/crear.html",
        {
            "form": form,
            "club": club,
        },
    )


@requerir_admin_club
def editar_usuario(request, perfil_id):
    club = obtener_club_usuario(request.user)

    perfil = get_object_or_404(
        PerfilUsuario.objects.select_related("usuario"),
        id=perfil_id,
        club=club,
    )

    usuario = perfil.usuario

    if request.method == "POST":
        form = EditarUsuarioClubForm(
            request.POST,
            usuario=usuario,
        )

        if form.is_valid():
            nuevo_rol = form.cleaned_data["rol"]
            nuevo_activo = form.cleaned_data["activo"]

            # Un administrador no puede quitarse a sí mismo el acceso
            # administrativo ni desactivar su propio perfil.
            if usuario == request.user and (
                nuevo_rol != PerfilUsuario.Rol.ADMIN
                or not nuevo_activo
            ):
                messages.error(
                    request,
                    (
                        "No podés quitarte a vos mismo el rol de administrador "
                        "ni desactivar tu propio usuario."
                    ),
                )

            # Tampoco permitimos dejar al club sin administradores activos.
            elif (
                perfil.rol == PerfilUsuario.Rol.ADMIN
                and perfil.activo
                and (
                    nuevo_rol != PerfilUsuario.Rol.ADMIN
                    or not nuevo_activo
                )
                and _es_ultimo_admin_activo(perfil)
            ):
                messages.error(
                    request,
                    (
                        "El club debe conservar al menos un administrador "
                        "activo. Asigná otro administrador antes de modificar "
                        "este usuario."
                    ),
                )

            else:
                with transaction.atomic():
                    usuario.first_name = form.cleaned_data["nombre"]
                    usuario.last_name = form.cleaned_data["apellido"]
                    usuario.email = form.cleaned_data["email"]
                    usuario.is_active = nuevo_activo

                    nueva_password = form.cleaned_data.get(
                        "nueva_password"
                    )

                    if nueva_password:
                        usuario.set_password(
                            nueva_password
                        )
                        usuario.save()
                    else:
                        usuario.save(
                            update_fields=[
                                "first_name",
                                "last_name",
                                "email",
                                "is_active",
                            ]
                        )

                    perfil.rol = nuevo_rol
                    perfil.activo = nuevo_activo
                    perfil.save(
                        update_fields=[
                            "rol",
                            "activo",
                        ]
                    )

                if nueva_password and usuario == request.user:
                    update_session_auth_hash(
                        request,
                        usuario,
                    )

                messages.success(
                    request,
                    (
                        f'El usuario "{usuario.username}" '
                        "se actualizó correctamente."
                    ),
                )

                return redirect("lista_usuarios")

    else:
        form = EditarUsuarioClubForm(
            usuario=usuario,
            initial={
                "nombre": usuario.first_name,
                "apellido": usuario.last_name,
                "email": usuario.email,
                "rol": perfil.rol,
                "activo": perfil.activo,
            }
        )

    return render(
        request,
        "clubs/usuarios/editar.html",
        {
            "form": form,
            "club": club,
            "perfil": perfil,
            "usuario_editado": usuario,
        },
    )


@requerir_admin_club
@require_POST
def cambiar_estado_usuario(
    request,
    perfil_id,
):
    club = obtener_club_usuario(request.user)

    perfil = get_object_or_404(
        PerfilUsuario.objects.select_related("usuario"),
        id=perfil_id,
        club=club,
    )

    if perfil.usuario == request.user:
        messages.error(
            request,
            (
                "No podés desactivar tu propio usuario "
                "desde esta pantalla."
            ),
        )

        return redirect("lista_usuarios")

    nuevo_estado = not perfil.activo

    if (
        not nuevo_estado
        and _es_ultimo_admin_activo(perfil)
    ):
        messages.error(
            request,
            (
                "No podés desactivar al último administrador activo del club. "
                "Asigná otro administrador antes de continuar."
            ),
        )

        return redirect("lista_usuarios")

    with transaction.atomic():
        perfil.activo = nuevo_estado
        perfil.save(
            update_fields=["activo"],
        )

        perfil.usuario.is_active = nuevo_estado
        perfil.usuario.save(
            update_fields=["is_active"],
        )

    if perfil.activo:
        mensaje = (
            f'El usuario "{perfil.usuario.username}" '
            "fue activado."
        )
    else:
        mensaje = (
            f'El usuario "{perfil.usuario.username}" '
            "fue desactivado."
        )

    messages.success(
        request,
        mensaje,
    )

    return redirect("lista_usuarios")


@requerir_club
def mi_perfil(request):
    """
    Perfil personal del usuario comercial.

    Tanto administradores como entrenadores pueden editar únicamente
    sus propios datos personales.
    """
    club = obtener_club_usuario(request.user)
    perfil = request.user.perfil_club

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(
                request,
                "El email es obligatorio.",
            )
        elif (
            User.objects
            .filter(email__iexact=email)
            .exclude(pk=request.user.pk)
            .exists()
        ):
            messages.error(
                request,
                "Ya existe otro usuario con ese email.",
            )
        else:
            request.user.first_name = nombre
            request.user.last_name = apellido
            request.user.email = email
            request.user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )

            messages.success(
                request,
                "Tu perfil se actualizó correctamente.",
            )

            return redirect("mi_perfil")

    return render(
        request,
        "clubs/mi_perfil.html",
        {
            "club": club,
            "perfil": perfil,
        },
    )


def registro_club_invitacion(request, token):
    """
    Alta autoservicio de un club mediante una invitación única.
    Una invitación inexistente o ya utilizada muestra una pantalla amigable.
    """
    invitacion = (
        InvitacionClub.objects
        .filter(token=token)
        .first()
    )

    if invitacion is None or invitacion.usada:
        return render(
            request,
            "clubs/invitacion_expirada.html",
            status=410,
        )

    if request.user.is_authenticated:
        return redirect("configuracion_club")

    if request.method == "POST":
        form = RegistroClubInvitacionForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            with transaction.atomic():
                invitacion_bloqueada = (
                    InvitacionClub.objects
                    .select_for_update()
                    .filter(
                        pk=invitacion.pk,
                        usada_en__isnull=True,
                    )
                    .first()
                )

                if invitacion_bloqueada is None:
                    return render(
                        request,
                        "clubs/invitacion_expirada.html",
                        status=410,
                    )

                club = Club.objects.create(
                    nombre=form.cleaned_data["nombre_club"],
                    logo=form.cleaned_data.get("logo"),
                    color_primario=form.cleaned_data["color_primario"],
                    color_secundario=form.cleaned_data["color_secundario"],
                    email=form.cleaned_data.get("email_club", ""),
                    activo=True,
                    estado_pago=Club.EstadoPago.PENDIENTE,
                )

                usuario = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    first_name=form.cleaned_data["nombre_admin"],
                    last_name=form.cleaned_data["apellido_admin"],
                    email=form.cleaned_data["email_admin"],
                    password=form.cleaned_data["password"],
                    is_active=True,
                )

                PerfilUsuario.objects.create(
                    usuario=usuario,
                    club=club,
                    rol=PerfilUsuario.Rol.ADMIN,
                    activo=True,
                )

                invitacion_bloqueada.usada_en = timezone.now()
                invitacion_bloqueada.club_creado = club
                invitacion_bloqueada.save(
                    update_fields=[
                        "usada_en",
                        "club_creado",
                    ]
                )

            login(request, usuario)

            messages.success(
                request,
                (
                    f'El club "{club.nombre}" se creó correctamente. '
                    "Ya podés completar la configuración inicial."
                ),
            )

            return redirect("onboarding_club")

    else:
        form = RegistroClubInvitacionForm()

    return render(
        request,
        "clubs/registro_invitacion.html",
        {
            "form": form,
            "invitacion": invitacion,
        },
    )

@requerir_admin_club
def onboarding_club(request):
    """
    Checklist de puesta en marcha del club.
    Se calcula automáticamente a partir de los datos reales del club.
    """
    from asistencia.models import (
        CategoriaEjercicio,
        Ejercicio,
        Entrenamiento,
        Jugador,
    )

    club = obtener_club_usuario(request.user)

    tiene_turnos = TurnoClub.objects.filter(
        club=club,
        activo=True,
    ).exists()

    tiene_entrenadores = PerfilUsuario.objects.filter(
        club=club,
        rol=PerfilUsuario.Rol.ENTRENADOR,
        activo=True,
        usuario__is_active=True,
    ).exists()

    tiene_jugadores = Jugador.objects.filter(
        club=club,
        activo=True,
    ).exists()

    tiene_categorias = CategoriaEjercicio.objects.filter(
        club=club,
        activo=True,
    ).exists()

    tiene_ejercicios = Ejercicio.objects.filter(
        club=club,
        activo=True,
    ).exists()

    tiene_biblioteca = (
        tiene_categorias
        and tiene_ejercicios
    )

    tiene_entrenamientos = Entrenamiento.objects.filter(
        club=club,
    ).exists()

    pasos = [
        {
            "titulo": "Club creado",
            "descripcion": (
                "El nombre, los colores y la cuenta administradora "
                "ya están configurados."
            ),
            "completo": True,
            "url": reverse("configuracion_club"),
            "boton": "Revisar configuración",
        },
        {
            "titulo": "Crear el primer turno",
            "descripcion": (
                "Definí los días y horarios en los que entrena el club."
            ),
            "completo": tiene_turnos,
            "url": reverse("crear_turno"),
            "boton": "Crear turno",
        },
        {
            "titulo": "Agregar entrenadores",
            "descripcion": (
                "Creá los accesos para las personas que van a trabajar "
                "con los entrenamientos."
            ),
            "completo": tiene_entrenadores,
            "url": reverse("crear_usuario"),
            "boton": "Agregar entrenador",
        },
        {
            "titulo": "Cargar jugadores",
            "descripcion": (
                "Agregá al menos un jugador para empezar a armar "
                "los entrenamientos."
            ),
            "completo": tiene_jugadores,
            "url": reverse("crear_jugador"),
            "boton": "Agregar jugador",
        },
        {
            "titulo": "Crear categorías y ejercicios",
            "descripcion": (
                "Armá la biblioteca de ejercicios que va a usar el club."
            ),
            "completo": tiene_biblioteca,
            "url": reverse("lista_ejercicios"),
            "boton": "Configurar ejercicios",
        },
        {
            "titulo": "Registrar el primer entrenamiento",
            "descripcion": (
                "Cuando lo anterior esté listo, ya podés empezar "
                "a usar la carga diaria."
            ),
            "completo": tiene_entrenamientos,
            "url": reverse("inicio"),
            "boton": "Ir a carga diaria",
        },
    ]

    completados = sum(
        1
        for paso in pasos
        if paso["completo"]
    )

    total = len(pasos)

    porcentaje = int(
        completados * 100 / total
    )

    return render(
        request,
        "clubs/onboarding.html",
        {
            "club": club,
            "pasos": pasos,
            "completados": completados,
            "total": total,
            "porcentaje": porcentaje,
            "onboarding_completo": completados == total,
        },
    )

