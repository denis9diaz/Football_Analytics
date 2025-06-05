from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis
from random import uniform

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método Over 0.5 HT'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        metodo = MetodoAnalisis.objects.get(nombre__iexact='Over 0.5 HT')

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
            temporadas_validas = [temporada_actual - i for i in range(3)]  # máx. 2 temporadas anteriores

            def calcular_prob(equipo):
                historial = Partido.objects.filter(
                    (Q(equipo_local=equipo) | Q(equipo_visitante=equipo)),
                    goles_local_ht__isnull=False,
                    goles_visitante_ht__isnull=False,
                    fecha__lt=partido.fecha,
                    liga=liga_actual,
                    fecha__year__in=temporadas_validas,
                ).order_by('-fecha')

                total = historial.count()
                if total == 0:
                    return None  # sin datos, omitir

                cumple = [(p.goles_local_ht + p.goles_visitante_ht) > 0 for p in historial]
                porcentaje = sum(cumple) / total

                if not cumple[0]:
                    racha = next((i for i, ok in enumerate(cumple) if ok), len(cumple))
                    return 1 - ((1 - porcentaje) ** (racha + 1))
                return porcentaje

            probs = [p for p in [calcular_prob(local), calcular_prob(visitante)] if p is not None]
            if not probs:
                self.stdout.write(self.style.WARNING(f"{partido}: Sin datos suficientes"))
                continue

            prob_media = sum(probs) / len(probs)
            cuota_real = round(1 / prob_media, 2) if prob_media > 0 else 99.99
            cuota_casa = round(max(cuota_real + uniform(-0.3, 0.3), 1.00), 2)
            valor_estimado = round((cuota_casa / cuota_real - 1) * 100, 2)

            PartidoAnalisis.objects.create(
                metodo=metodo,
                partido=partido,
                cuota_estim_real=cuota_real,
                cuota_casa_apuestas=cuota_casa,
                valor_estimado=valor_estimado,
                porcentaje_acierto=round(prob_media * 100, 2),
            )

            self.stdout.write(self.style.SUCCESS(
                f"{partido} -> Over 0.5 HT: {round(prob_media*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor_estimado}%"
            ))
