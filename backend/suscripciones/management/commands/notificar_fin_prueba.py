from django.core.management.base import BaseCommand
from django.utils.timezone import now
from suscripciones.models import Suscripcion
from suscripciones.views import enviar_email_suscripcion

class Command(BaseCommand):
    help = 'Notifica a los usuarios cuando finaliza su prueba gratuita'

    def handle(self, *args, **kwargs):
        hoy = now().date()

        pruebas_finalizadas = Suscripcion.objects.filter(
            plan='prueba',
            fecha_fin__lte=hoy,
            cancelada=False
        )

        for s in pruebas_finalizadas:
            # Marcar como cancelada y enviar notificación
            s.cancelada = True
            s.save()
            enviar_email_suscripcion(s.usuario, "fin_prueba")
            self.stdout.write(f"Notificada prueba finalizada: {s.usuario.username}")
