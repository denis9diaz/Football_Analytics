from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from analisis.models import Partido
from analisis.utils.api_fixtures_fecha import fetch_fixtures_por_fecha
from datetime import datetime

LIGAS = {
    245: "Ykkönen",
    1087: "Ykösliiga",
}

class Command(BaseCommand):
    help = 'Importa resultados de partidos de una fecha concreta en las ligas seleccionadas (formato YYYY-MM-DD)'

    def add_arguments(self, parser):
        parser.add_argument('fecha', type=str, help='Fecha en formato YYYY-MM-DD')

    def handle(self, *args, **options):
        fecha_objetivo = options['fecha']
        total_actualizados = 0

        try:
            datetime.strptime(fecha_objetivo, "%Y-%m-%d")
        except ValueError:
            self.stderr.write("❌ Formato de fecha inválido. Usa YYYY-MM-DD.")
            return

        for liga_id, liga_nombre in LIGAS.items():
            self.stdout.write(f"📡 Llamando a fixtures de {liga_nombre} ({fecha_objetivo})...")
            data = fetch_fixtures_por_fecha(liga_id, fecha_objetivo, temporada=2025)
            actualizados = 0

            for item in data["response"]:
                fixture = item["fixture"]
                teams = item["teams"]
                score = item["score"]

                partido_id = str(fixture["id"])

                try:
                    partido = Partido.objects.get(codigo_api=partido_id)
                except Partido.DoesNotExist:
                    continue

                if score["fulltime"]["home"] is None or score["fulltime"]["away"] is None:
                    continue

                partido.goles_local_ht = score["halftime"]["home"]
                partido.goles_visitante_ht = score["halftime"]["away"]
                partido.goles_local_ft = score["fulltime"]["home"]
                partido.goles_visitante_ft = score["fulltime"]["away"]

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
                self.stdout.write(f"✅ {teams['home']['name']} vs {teams['away']['name']} actualizado.")

            total_actualizados += actualizados
            self.stdout.write(f"🟩 {liga_nombre}: {actualizados} partidos actualizados.\n")

        self.stdout.write(f"✅ PROCESO COMPLETO. Total de partidos actualizados: {total_actualizados}")
