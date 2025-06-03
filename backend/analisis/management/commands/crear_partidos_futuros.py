from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from random import shuffle
from analisis.models import Liga, Equipo, Partido

class Command(BaseCommand):
    help = "Crea 5 jornadas sin resultados desde hoy hasta el domingo para todas las ligas"

    def handle(self, *args, **kwargs):
        hoy = now().date()
        fechas = [hoy + timedelta(days=i) for i in range(5)]  # Hoy hasta domingo

        for liga in Liga.objects.all():
            equipos = list(Equipo.objects.filter(liga=liga))
            num_equipos = len(equipos)

            if num_equipos < 2:
                self.stdout.write(self.style.WARNING(f"⚠️ Liga '{liga.nombre}' ignorada: menos de 2 equipos"))
                continue

            enfrentamientos_previos = set(
                Partido.objects.filter(liga=liga)
                .values_list("equipo_local_id", "equipo_visitante_id")
            )

            for dia, fecha in enumerate(fechas):
                shuffle(equipos)
                usados = set()
                partidos_dia = []

                for i in range(0, num_equipos - 1, 2):
                    local = equipos[i]
                    visitante = equipos[i + 1]

                    ya_jugado = (
                        (local.id, visitante.id) in enfrentamientos_previos or
                        (visitante.id, local.id) in enfrentamientos_previos
                    )

                    if (local in usados or visitante in usados) or ya_jugado:
                        continue

                    usados.add(local)
                    usados.add(visitante)
                    partidos_dia.append((local, visitante))
                    enfrentamientos_previos.add((local.id, visitante.id))

                for local, visitante in partidos_dia:
                    Partido.objects.create(
                        liga=liga,
                        equipo_local=local,
                        equipo_visitante=visitante,
                        fecha=now().replace(
                            year=fecha.year, month=fecha.month, day=fecha.day,
                            hour=20, minute=0, second=0, microsecond=0
                        )
                        # No añadimos goles ni estadísticas
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"{fecha.strftime('%Y-%m-%d')} | {liga.nombre} | {local.nombre} vs {visitante.nombre}"
                    ))
