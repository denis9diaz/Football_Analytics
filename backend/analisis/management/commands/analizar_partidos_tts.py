from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q
from random import uniform
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método TTS (Team To Score)'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        metodo = MetodoAnalisis.objects.get(nombre__iexact='TTS')

        partidos_hoy = Partido.objects.filter(fecha__date=hoy)

        for partido in partidos_hoy:
            ya_creados = PartidoAnalisis.objects.filter(
                metodo=metodo,
                partido=partido
            ).values_list('equipo_destacado', flat=True)

            if 'local' in ya_creados and 'visitante' in ya_creados:
                continue

            local = partido.equipo_local
            visitante = partido.equipo_visitante

            def calcular_prob_marcar(equipo, contexto='local'):
                if not equipo:
                    return 0.5

                if contexto == 'local':
                    partidos_jugados = Partido.objects.filter(
                        equipo_local=equipo,
                        marco_local__isnull=False
                    ).order_by('-fecha')
                    marcados = partidos_jugados.filter(marco_local=True)
                else:
                    partidos_jugados = Partido.objects.filter(
                        equipo_visitante=equipo,
                        marco_visitante__isnull=False
                    ).order_by('-fecha')
                    marcados = partidos_jugados.filter(marco_visitante=True)

                total = partidos_jugados.count()
                if total == 0:
                    return 0.5

                porcentaje = marcados.count() / total

                ultimos = partidos_jugados[:3]
                sin_marcar = sum([
                    not p.marco_local if contexto == 'local' else not p.marco_visitante
                    for p in ultimos
                ])

                if sin_marcar > 0:
                    prob = 1 - ((1 - porcentaje) ** (sin_marcar + 1))
                else:
                    prob = porcentaje

                return prob

            # LOCAL MARCA
            if 'local' not in ya_creados:
                prob_local = (
                    calcular_prob_marcar(local, 'local') +
                    calcular_prob_marcar(visitante, 'visitante')
                ) / 2

                cuota_real = round(1 / prob_local, 2) if prob_local > 0 else 99.99
                cuota_casa = round(max(cuota_real + uniform(-0.25, 0.25), 1.00), 2)
                valor = round((cuota_casa / cuota_real - 1) * 100, 2)

                PartidoAnalisis.objects.create(
                    metodo=metodo,
                    partido=partido,
                    cuota_estim_real=cuota_real,
                    cuota_casa_apuestas=cuota_casa,
                    valor_estimado=valor,
                    porcentaje_acierto=round(prob_local * 100, 2),
                    equipo_destacado='local'
                )

                self.stdout.write(self.style.SUCCESS(
                    f"{partido} -> prob: {round(prob_local*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor}%"
                ))

            # VISITANTE MARCA
            if 'visitante' not in ya_creados:
                prob_visit = (
                    calcular_prob_marcar(visitante, 'visitante') +
                    calcular_prob_marcar(local, 'local')
                ) / 2

                cuota_real = round(1 / prob_visit, 2) if prob_visit > 0 else 99.99
                cuota_casa = round(max(cuota_real + uniform(-0.25, 0.25), 1.00), 2)
                valor = round((cuota_casa / cuota_real - 1) * 100, 2)

                PartidoAnalisis.objects.create(
                    metodo=metodo,
                    partido=partido,
                    cuota_estim_real=cuota_real,
                    cuota_casa_apuestas=cuota_casa,
                    valor_estimado=valor,
                    porcentaje_acierto=round(prob_visit * 100, 2),
                    equipo_destacado='visitante'
                )

                self.stdout.write(self.style.SUCCESS(
                    f"{partido} -> prob: {round(prob_visit*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor}%"
                ))
