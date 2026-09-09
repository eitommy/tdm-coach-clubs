from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Administración de Django
    path(
        "admin/",
        admin.site.urls,
    ),

    # Login / logout / cambio de contraseña
    path(
        "accounts/",
        include("django.contrib.auth.urls"),
    ),

    # Administración del club
    path(
        "club/",
        include("clubs.urls"),
    ),

    # App principal de entrenamientos
    path(
        "",
        include("asistencia.urls"),
    ),
]


# Archivos subidos durante desarrollo local
# Ejemplo: logos de los clubes.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )