from django.core.management.base import BaseCommand
from analisis.utils.api_fixtures_futures import fetch_fixtures_futuros
from analisis.models import Liga, Equipo, Partido
from django.utils.dateparse import parse_datetime

LIGAS = {
    140: "La Liga",
    141: "Segunda División",
}

TEMPORADA = "2025"

class Command(BaseCommand):
    help = 'Importa partidos FUTUROS desde la API de API-Football (sin resultado)'

    def handle(self, *args, **kwargs):
        total_partidos = 0
        for liga_id, liga_nombre in LIGAS.items():
            self.stdout.write(f"📡 Llamando a futuros de {liga_nombre} ({TEMPORADA})...")
            data = fetch_fixtures_futuros(liga_id, TEMPORADA)

            partidos_guardados = 0

            for item in data["response"]:
                fixture = item["fixture"]
                league = item["league"]
                teams = item["teams"]

                fecha = parse_datetime(fixture["date"])
                cod_partido = str(fixture["id"])

                # Crear liga si no existe
                liga_obj, _ = Liga.objects.get_or_create(
                    codigo_api=str(league["id"]),
                    defaults={
                        "nombre": league["name"],
                        "codigo_pais": league["country"][:6]
                    }
                )

                # Crear equipos si no existen
                equipo_local, _ = Equipo.objects.get_or_create(
                    codigo_api=str(teams["home"]["id"]),
                    defaults={"nombre": teams["home"]["name"]}
                )
                if not equipo_local.ligas.filter(id=liga_obj.id).exists():
                    equipo_local.ligas.add(liga_obj)

                equipo_visitante, _ = Equipo.objects.get_or_create(
                    codigo_api=str(teams["away"]["id"]),
                    defaults={"nombre": teams["away"]["name"]}
                )
                if not equipo_visitante.ligas.filter(id=liga_obj.id).exists():
                    equipo_visitante.ligas.add(liga_obj)

                # Evita duplicados
                if Partido.objects.filter(codigo_api=cod_partido).exists():
                    continue

                # Crear partido sin resultado
                Partido.objects.create(
                    codigo_api=cod_partido,
                    liga=liga_obj,
                    equipo_local=equipo_local,
                    equipo_visitante=equipo_visitante,
                    fecha=fecha,
                    goles_local_ht=None,
                    goles_visitante_ht=None,
                    goles_local_ft=None,
                    goles_visitante_ft=None,
                    resultado_1x2=None,
                    btts=None,
                    over_1_5=None,
                    over_2_5=None,
                    marco_local=None,
                    marco_visitante=None,
                    over_1_5_local=None
                )

                partidos_guardados += 1
                self.stdout.write(f"✅ {equipo_local.nombre} vs {equipo_visitante.nombre} ({fecha.date()})")

            total_partidos += partidos_guardados
            self.stdout.write(f"🟩 {liga_nombre} completada. Partidos futuros guardados: {partidos_guardados}\n")

        self.stdout.write(f"✅ PROCESO COMPLETO. Total de partidos futuros guardados: {total_partidos}")
