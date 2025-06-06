from django.core.management.base import BaseCommand
from analisis.models import Partido, RachaEquipo

class Command(BaseCommand):
    help = "Recalcula todas las rachas actuales ejecutando save() en cada partido"

    def handle(self, *args, **kwargs):
        self.stdout.write("⏳ Borrando rachas actuales...")
        RachaEquipo.objects.filter(tipo='actual').delete()

        self.stdout.write("📊 Recalculando rachas actuales...")
        partidos = Partido.objects.filter(goles_local_ft__isnull=False, goles_visitante_ft__isnull=False).order_by("fecha")

        for i, partido in enumerate(partidos):
            partido.save()
            if i % 100 == 0:
                self.stdout.write(f"  > {i+1} partidos procesados...")

        self.stdout.write("✅ Rachas actuales recalculadas correctamente.")
