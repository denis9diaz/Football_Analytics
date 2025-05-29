from django.core.management.base import BaseCommand
from django.utils.timezone import now
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

            def calcular_prob_marcar(equipo, contexto, fecha_limite):
                if contexto == 'local':
                    partidos = Partido.objects.filter(
                        equipo_local=equipo,
                        marco_local__isnull=False,
                        fecha__lt=fecha_limite
                    ).order_by('-fecha')
                    goles = 'marco_local'
                elif contexto == 'visitante':
                    partidos = Partido.objects.filter(
                        equipo_visitante=equipo,
                        marco_visitante__isnull=False,
                        fecha__lt=fecha_limite
                    ).order_by('-fecha')
                    goles = 'marco_visitante'
                elif contexto == 'local_recibe':
                    partidos = Partido.objects.filter(
                        equipo_local=equipo,
                        marco_visitante__isnull=False,
                        fecha__lt=fecha_limite
                    ).order_by('-fecha')
                    goles = 'marco_visitante'
                elif contexto == 'visitante_recibe':
                    partidos = Partido.objects.filter(
                        equipo_visitante=equipo,
                        marco_local__isnull=False,
                        fecha__lt=fecha_limite
                    ).order_by('-fecha')
                    goles = 'marco_local'
                else:
                    return 0.0

                total = partidos.count()
                if total == 0:
                    self.stdout.write(f"🔍 {equipo} [{contexto}] → sin partidos anteriores válidos")
                    return 0.0

                self.stdout.write(f"\n🔎 {equipo} [{contexto}] - partidos analizados:")
                for p in partidos:
                    valor = getattr(p, goles)
                    self.stdout.write(f"  • {p.fecha} vs {p.equipo_local} - {p.equipo_visitante} → {'✅' if valor else '❌'}")

                marcados = partidos.filter(**{goles: True})
                porcentaje = marcados.count() / total

                racha = 0
                for p in partidos:
                    if getattr(p, goles):
                        break
                    racha += 1

                if racha > 0:
                    prob = 1 - ((1 - porcentaje) ** (racha + 1))
                else:
                    prob = porcentaje

                self.stdout.write(f"👉 % marcados: {round(porcentaje*100,2)}%, racha sin marcar: {racha}, prob final: {round(prob*100,2)}%\n")
                return prob

            # LOCAL MARCA
            if 'local' not in ya_creados:
                self.stdout.write(f"\n🟦 Análisis LOCAL: {partido}")
                prob_local = (
                    calcular_prob_marcar(local, 'local', partido.fecha) +
                    calcular_prob_marcar(visitante, 'visitante_recibe', partido.fecha)
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
                    f"{partido} (LOCAL marca) -> prob: {round(prob_local*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor}%"
                ))

            # VISITANTE MARCA
            if 'visitante' not in ya_creados:
                self.stdout.write(f"\n🟥 Análisis VISITANTE: {partido}")
                prob_visit = (
                    calcular_prob_marcar(visitante, 'visitante', partido.fecha) +
                    calcular_prob_marcar(local, 'local_recibe', partido.fecha)
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
                    f"{partido} (VISITANTE marca) -> prob: {round(prob_visit*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa}, valor: {valor}%"
                ))
