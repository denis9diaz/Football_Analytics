from django.core.management.base import BaseCommand
from analisis.utils.actualizar_rachas import actualizar_rachas

class Command(BaseCommand):
    help = "Recalcula todas las rachas de todos los equipos"

    def handle(self, *args, **kwargs):
        self.stdout.write("Recalculando todas las rachas...")
        actualizar_rachas()
        self.stdout.write("Rachas recalculadas correctamente.")
