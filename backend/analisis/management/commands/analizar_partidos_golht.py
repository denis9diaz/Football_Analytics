from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis
from random import uniform

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método Gol HT'

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

            historial_local = Partido.objects.filter(
                Q(equipo_local=local) | Q(equipo_visitante=local),
                goles_local_ht__isnull=False,
                goles_visitante_ht__isnull=False
            ).order_by('-fecha')

            historial_visitante = Partido.objects.filter(
                Q(equipo_local=visitante) | Q(equipo_visitante=visitante),
                goles_local_ht__isnull=False,
                goles_visitante_ht__isnull=False
            ).order_by('-fecha')

            def calcular_prob(historial):
                total = historial.count()
                if total == 0:
                    return 0.5

                con_gol = sum(1 for p in historial if (p.goles_local_ht + p.goles_visitante_ht) > 0)
                porcentaje = con_gol / total

                ultimo = historial.first()
                if ultimo and (ultimo.goles_local_ht + ultimo.goles_visitante_ht == 0):
                    prob = 1 - (1 - porcentaje) ** 2
                else:
                    prob = porcentaje

                return prob

            prob_local = calcular_prob(historial_local)
            prob_visitante = calcular_prob(historial_visitante)

            prob_media = (prob_local + prob_visitante) / 2
            cuota_real = round(1 / prob_media, 2) if prob_media > 0 else 99.99
            cuota_casa = round(max(cuota_real + uniform(-0.3, 0.3), 1.00), 2)
            valor_estimado = round(( cuota_casa / cuota_real - 1) * 100, 2)

            PartidoAnalisis.objects.create(
                metodo=metodo,
                partido=partido,
                cuota_estim_real=cuota_real,
                cuota_casa_apuestas=cuota_casa,
                valor_estimado=valor_estimado,
                porcentaje_acierto=round(prob_media * 100, 2),
            )

            self.stdout.write(self.style.SUCCESS(
                f"{partido} -> prob: {round(prob_media*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor_estimado}%"
            ))
