from django.core.management.base import BaseCommand
from analisis.utils.api import fetch_fixtures
from analisis.models import Liga, Equipo, Partido
from django.utils.dateparse import parse_datetime

LIGAS = {
    1087: "Ykkösliiga",
}

TEMPORADAS = ["2023", "2024", "2025"]

class Command(BaseCommand):
    help = 'Importa partidos reales desde la API de API-Football'

    def handle(self, *args, **kwargs):
        total_partidos = 0
        for liga_id, liga_nombre in LIGAS.items():
            for temporada in TEMPORADAS:
                self.stdout.write(f"📡 Llamando a fixtures de {liga_nombre} ({temporada})...")
                data = fetch_fixtures(liga_id, temporada)

                partidos_guardados = 0

                for item in data["response"]:
                    fixture = item["fixture"]
                    league = item["league"]
                    teams = item["teams"]
                    goals = item["goals"]
                    score = item["score"]

                    # Crear liga si no existe
                    liga_obj, _ = Liga.objects.get_or_create(
                        codigo_api=str(league["id"]),
                        defaults={
                            "nombre": league["name"],
                            "codigo_pais": league["country"][:6]
                        }
                    )

                    # Crear equipos si no existen y asociarlos a la liga si aún no están vinculados
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


                    # Extraer datos
                    goles_local_ht = score["halftime"]["home"]
                    goles_visitante_ht = score["halftime"]["away"]
                    goles_local_ft = score["fulltime"]["home"]
                    goles_visitante_ft = score["fulltime"]["away"]

                    if goles_local_ft is None or goles_visitante_ft is None:
                        continue  # saltamos partidos sin resultado final

                    resultado_1x2 = (
                        '1' if goles_local_ft > goles_visitante_ft else
                        '2' if goles_visitante_ft > goles_local_ft else 'X'
                    )

                    partido, creado = Partido.objects.get_or_create(
                        codigo_api=str(fixture["id"]),
                        defaults={
                            "liga": liga_obj,
                            "equipo_local": equipo_local,
                            "equipo_visitante": equipo_visitante,
                            "fecha": parse_datetime(fixture["date"]),
                            "goles_local_ht": goles_local_ht,
                            "goles_visitante_ht": goles_visitante_ht,
                            "goles_local_ft": goles_local_ft,
                            "goles_visitante_ft": goles_visitante_ft,
                            "resultado_1x2": resultado_1x2,
                            "btts": goles_local_ft > 0 and goles_visitante_ft > 0,
                            "over_1_5": (goles_local_ft + goles_visitante_ft) > 1.5,
                            "over_2_5": (goles_local_ft + goles_visitante_ft) > 2.5,
                            "marco_local": goles_local_ft > 0,
                            "marco_visitante": goles_visitante_ft > 0,
                            "over_1_5_local": goles_local_ft >= 2
                        }
                    )

                    if creado:
                        partidos_guardados += 1
                        self.stdout.write(f"✅ {equipo_local.nombre} vs {equipo_visitante.nombre} ({fixture['date']})")

                total_partidos += partidos_guardados
                self.stdout.write(f"🟩 Temporada {temporada} de {liga_nombre} completada. Partidos guardados: {partidos_guardados}\n")

        self.stdout.write(f"✅ PROCESO COMPLETO. Total de partidos guardados: {total_partidos}")
