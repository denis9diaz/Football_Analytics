from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q
from random import uniform
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método Over 1.5 Goles'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        metodo = MetodoAnalisis.objects.get(nombre__iexact='Over 1.5')

        partidos_hoy = Partido.objects.filter(
            fecha__date=hoy
        ).exclude(
            id__in=PartidoAnalisis.objects.filter(metodo=metodo).values_list('partido_id', flat=True)
        )

        for partido in partidos_hoy:
            local = partido.equipo_local
            visitante = partido.equipo_visitante

            def calcular_prob(equipo, fecha_limite):
                historial = Partido.objects.filter(
                    Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
                    goles_local_ft__isnull=False,
                    goles_visitante_ft__isnull=False,
                    fecha__lt=fecha_limite
                ).order_by('-fecha')

                if not historial.exists():
                    return 0.0

                cumple = [
                    (p.goles_local_ft + p.goles_visitante_ft) > 1
                    for p in historial
                ]

                total = len(cumple)
                aciertos = sum(cumple)

                if aciertos == 0:
                    return 0.0

                porcentaje = aciertos / total

                if not cumple[0]:  # si el partido más reciente NO cumplió
                    racha = next((i for i, ok in enumerate(cumple) if ok), len(cumple))
                    return 1 - ((1 - porcentaje) ** (racha + 1))
                return porcentaje

            prob_local = calcular_prob(local, partido.fecha)
            prob_visit = calcular_prob(visitante, partido.fecha)
            prob_media = (prob_local + prob_visit) / 2

            cuota_real = round(1 / prob_media, 2) if prob_media > 0 else 99.99
            cuota_casa = round(max(cuota_real + uniform(-0.3, 0.3), 1.00), 2)
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
                f"{partido} -> Over 1.5: {round(prob_media*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor}%"
            ))
