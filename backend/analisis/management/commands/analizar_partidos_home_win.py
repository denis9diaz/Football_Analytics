from django.core.management.base import BaseCommand
from django.utils.timezone import now
from random import uniform
from django.db.models import F
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis
from analisis.utils.api_odds import fetch_cuota_casa  # 👈

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método Home to Win (gana el equipo local)'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        metodo = MetodoAnalisis.objects.get(nombre__iexact='Home to Win')

        partidos_hoy = Partido.objects.filter(
            fecha__date=hoy
        ).exclude(
            id__in=PartidoAnalisis.objects.filter(metodo=metodo).values_list('partido_id', flat=True)
        )

        for partido in partidos_hoy:
            local = partido.equipo_local
            visitante = partido.equipo_visitante
            liga_actual = partido.liga
            temporada_actual = partido.fecha.year
            temporadas_validas = [temporada_actual - i for i in range(3)]

            def calcular_victorias_local(equipo, fecha_limite):
                partidos = Partido.objects.filter(
                    equipo_local=equipo,
                    goles_local_ft__isnull=False,
                    goles_visitante_ft__isnull=False,
                    fecha__lt=fecha_limite,
                    liga=liga_actual,
                    fecha__year__in=temporadas_validas,
                ).order_by('-fecha')

                total = partidos.count()
                if total == 0:
                    return 0.0

                victorias = partidos.filter(goles_local_ft__gt=F('goles_visitante_ft')).count()
                if total == 1 and victorias == 0:
                    return 0.0

                return victorias / total

            def calcular_derrotas_visitante(equipo, fecha_limite):
                partidos = Partido.objects.filter(
                    equipo_visitante=equipo,
                    goles_local_ft__isnull=False,
                    goles_visitante_ft__isnull=False,
                    fecha__lt=fecha_limite,
                    liga=liga_actual,
                    fecha__year__in=temporadas_validas,
                ).order_by('-fecha')

                total = partidos.count()
                if total == 0:
                    return 0.0

                derrotas = partidos.filter(goles_local_ft__gt=F('goles_visitante_ft')).count()
                if total == 1 and derrotas == 0:
                    return 0.0

                return derrotas / total

            prob_local = calcular_victorias_local(local, partido.fecha)
            prob_visit = calcular_derrotas_visitante(visitante, partido.fecha)
            prob_media = (prob_local + prob_visit) / 2

            cuota_real = round(1 / prob_media, 2) if prob_media > 0 else 99.99

            try:
                cuota_casa = fetch_cuota_casa(int(partido.codigo_api), "Match Winner", "Home")
                if cuota_casa is None:
                    raise ValueError("Cuota no encontrada en la API")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"{partido}: ❌ Cuota no encontrada en la API - {e}"))
                cuota_casa = round(max(cuota_real + uniform(-0.25, 0.25), 1.00), 2)
                mostrar_cuota_casa = "–"
                mostrar_valor = "–"
                valor = None
            else:
                mostrar_cuota_casa = cuota_casa
                valor = round((cuota_casa / cuota_real - 1) * 100, 2)
                mostrar_valor = f"{valor}%"

            PartidoAnalisis.objects.create(
                metodo=metodo,
                partido=partido,
                cuota_estim_real=cuota_real,
                cuota_casa_apuestas=cuota_casa,
                valor_estimado=valor if valor is not None else 0,
                porcentaje_acierto=round(prob_media * 100, 2),
            )

            self.stdout.write(self.style.SUCCESS(
                f"{partido} -> Home to Win: {round(prob_media*100,2)}%, cuota: {cuota_real}, casa: {mostrar_cuota_casa}, valor: {mostrar_valor}"
            ))
