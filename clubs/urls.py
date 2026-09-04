from django.urls import path

from . import views


urlpatterns = [
    path(
        "configuracion/",
        views.configuracion_club,
        name="configuracion_club",
    ),
]