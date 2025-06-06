from django.core.management.base import BaseCommand
from analisis.utils.actualizar_rachas_historicas import actualizar_rachas_historicas

class Command(BaseCommand):
    help = "Recalcula solo las rachas históricas de todos los equipos"

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Recalculando rachas históricas...")
        actualizar_rachas_historicas()
        self.stdout.write("✅ Rachas históricas actualizadas correctamente.")
