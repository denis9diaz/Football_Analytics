from django.core.management.base import BaseCommand
from django.utils.timezone import localdate
from datetime import timedelta
from analisis.models import Partido
from analisis.utils.api_fixture_id import fetch_fixture_por_id  # Lo creamos ahora
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Actualiza resultados de partidos jugados ayer que aún no tienen resultado'

    def handle(self, *args, **kwargs):
        ayer = localdate() - timedelta(days=1)
        partidos_pendientes = Partido.objects.filter(
            goles_local_ft__isnull=True,
            fecha__date=ayer
        )

        total = partidos_pendientes.count()
        actualizados = 0

        self.stdout.write(f"🔍 Analizando {total} partidos pendientes del {ayer}...\n")

        for partido in partidos_pendientes:
            fixture_id = partido.codigo_api
            data = fetch_fixture_por_id(fixture_id)

            if not data or not data.get("response"):
                continue

            fixture = data["response"][0]
            score = fixture["score"]
            halftime = score["halftime"]
            fulltime = score["fulltime"]

            if fulltime["home"] is None or fulltime["away"] is None:
                continue

            partido.goles_local_ht = halftime["home"]
            partido.goles_visitante_ht = halftime["away"]
            partido.goles_local_ft = fulltime["home"]
            partido.goles_visitante_ft = fulltime["away"]

            partido.resultado_1x2 = (
                '1' if partido.goles_local_ft > partido.goles_visitante_ft else
                '2' if partido.goles_visitante_ft > partido.goles_local_ft else 'X'
            )

            total_goles = partido.goles_local_ft + partido.goles_visitante_ft
            partido.btts = partido.goles_local_ft > 0 and partido.goles_visitante_ft > 0
            partido.over_1_5 = total_goles > 1.5
            partido.over_2_5 = total_goles > 2.5
            partido.marco_local = partido.goles_local_ft > 0
            partido.marco_visitante = partido.goles_visitante_ft > 0
            partido.over_1_5_local = partido.goles_local_ft >= 2

            partido.save()
            actualizados += 1
            self.stdout.write(f"✅ Partido actualizado: {partido}")

        self.stdout.write(f"\n✅ PROCESO COMPLETO. Partidos actualizados: {actualizados} / {total}")
