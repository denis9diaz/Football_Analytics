from django.core.management.base import BaseCommand
from analisis.models import RachaEquipo

class Command(BaseCommand):
    help = "Elimina todas las rachas (actuales e históricas) de todos los equipos"

    def handle(self, *args, **kwargs):
        total = RachaEquipo.objects.count()
        RachaEquipo.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"✅ {total} rachas eliminadas correctamente."))
