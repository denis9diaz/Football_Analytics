from django.core.management.base import BaseCommand
from django.utils.timezone import now
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis
from analisis.utils.api import fetch_cuota_casa

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método BTTS (Both Teams To Score)'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        metodo = MetodoAnalisis.objects.get(nombre__iexact='BTTS')

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

            def calcular_btts(equipo, como_local):
                if como_local:
                    partidos = Partido.objects.filter(
                        equipo_local=equipo,
                        liga=liga_actual,
                        fecha__lt=partido.fecha,
                        fecha__year__in=temporadas_validas,
                        goles_local_ft__isnull=False,
                        goles_visitante_ft__isnull=False
                    ).order_by('-fecha')
                else:
                    partidos = Partido.objects.filter(
                        equipo_visitante=equipo,
                        liga=liga_actual,
                        fecha__lt=partido.fecha,
                        fecha__year__in=temporadas_validas,
                        goles_local_ft__isnull=False,
                        goles_visitante_ft__isnull=False
                    ).order_by('-fecha')

                total = partidos.count()
                if total == 0:
                    return 0.0

                cumple = [p.goles_local_ft > 0 and p.goles_visitante_ft > 0 for p in partidos]
                if total == 1 and not cumple[0]:
                    return 0.0

                return sum(cumple) / total

            prob_local = calcular_btts(local, como_local=True)
            prob_visit = calcular_btts(visitante, como_local=False)
            prob_media = (prob_local + prob_visit) / 2

            cuota_real = round(1 / prob_media, 2) if prob_media > 0 else 99.99

            try:
                cuota_casa = fetch_cuota_casa(int(partido.codigo_api), "Both Teams Score", "Yes")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Partido {partido.id}: Error al obtener cuota de casa - {e}"))
                cuota_casa = None

            if cuota_casa is None:
                self.stdout.write(self.style.WARNING(f"Partido {partido.id}: ❌ Cuota no encontrada en la API"))
                valor = None
            else:
                valor = round((cuota_casa / cuota_real - 1) * 100, 2)

            PartidoAnalisis.objects.create(
                metodo=metodo,
                partido=partido,
                cuota_estim_real=cuota_real,
                cuota_casa_apuestas=cuota_casa,
                valor_estimado=valor,
                porcentaje_acierto=round(prob_media * 100, 2),
            )

            self.stdout.write(self.style.SUCCESS(
                f"Partido {partido.id} -> BTTS: {round(prob_media*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa if cuota_casa is not None else '–'}, valor: {valor if valor is not None else '–'}%"
            ))
