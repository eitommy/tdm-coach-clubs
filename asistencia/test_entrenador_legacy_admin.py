from django.contrib import admin
from django.test import SimpleTestCase

from asistencia.models import Entrenador


class EntrenadorLegacyAdminTests(SimpleTestCase):
    def test_entrenador_legacy_no_esta_registrado_en_admin(self):
        self.assertNotIn(
            Entrenador,
            admin.site._registry,
            msg=(
                "El modelo Entrenador es legacy/histórico y no debe "
                "estar disponible para crear o editar entrenadores "
                "comerciales desde Django admin."
            ),
        )
