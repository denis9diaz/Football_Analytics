from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from random import randint, shuffle, random
from analisis.models import Liga, Equipo, Partido

class Command(BaseCommand):
    help = "Genera 5 jornadas con datos realistas y coherentes para todas las ligas"

    def handle(self, *args, **kwargs):
        ligas = Liga.objects.all()
        fecha_base = (now() - timedelta(days=5)).replace(hour=20, minute=0, second=0, microsecond=0)

        for liga in ligas:
            equipos = list(Equipo.objects.filter(liga=liga))
            num_equipos = len(equipos)

            if num_equipos < 4:
                self.stdout.write(self.style.WARNING(f"⚠️ Liga '{liga.nombre}' ignorada: solo {num_equipos} equipos"))
                continue

            partidos_generados = set()
            jornada = 0

            while jornada < 5:
                shuffle(equipos)
                jornada_partidos = []
                usados_en_jornada = set()

                for i in range(0, num_equipos - 1, 2):
                    local = equipos[i]
                    visitante = equipos[i + 1]

                    # Evita duplicados
                    if (
                        (local.id, visitante.id) in partidos_generados or
                        (visitante.id, local.id) in partidos_generados or
                        local in usados_en_jornada or
                        visitante in usados_en_jornada
                    ):
                        continue

                    jornada_partidos.append((local, visitante))
                    partidos_generados.add((local.id, visitante.id))
                    usados_en_jornada.add(local)
                    usados_en_jornada.add(visitante)

                for idx, (local, visitante) in enumerate(jornada_partidos):
                    fecha = fecha_base + timedelta(days=(jornada * 1), minutes=idx * 7)

                    # Determinar si habrá gol HT (~70%)
                    gol_ht = random() < 0.7
                    goles_ht_local = randint(0, 1) if gol_ht else 0
                    goles_ht_visitante = randint(0, 1) if gol_ht else 0

                    # Goles FT (añadir 0-2 más goles)
                    goles_local_ft = goles_ht_local + randint(0, 2)
                    goles_visitante_ft = goles_ht_visitante + randint(0, 2)

                    total_goles = goles_local_ft + goles_visitante_ft
                    resultado = (
                        '1' if goles_local_ft > goles_visitante_ft else
                        '2' if goles_visitante_ft > goles_local_ft else
                        'X'
                    )

                    # Over / BTTS con probabilidad realista
                    over_1_5 = total_goles >= 2 or random() < 0.05  # Forzar algunos falsos positivos
                    over_2_5 = total_goles >= 3 if random() < 0.5 else False
                    btts = goles_local_ft > 0 and goles_visitante_ft > 0 if random() < 0.6 else False

                    partido = Partido.objects.create(
                        liga=liga,
                        equipo_local=local,
                        equipo_visitante=visitante,
                        fecha=fecha,
                        goles_local_ht=goles_ht_local,
                        goles_visitante_ht=goles_ht_visitante,
                        goles_local_ft=goles_local_ft,
                        goles_visitante_ft=goles_visitante_ft,
                        resultado_1x2=resultado,
                        over_1_5=over_1_5,
                        over_2_5=over_2_5,
                        btts=btts,
                        over_1_5_local=goles_local_ft >= 2
                    )
                    partido.save()

                    self.stdout.write(self.style.SUCCESS(
                        f"{liga.nombre} | {local.nombre} {goles_local_ft}-{goles_visitante_ft} {visitante.nombre}"
                    ))

                jornada += 1
