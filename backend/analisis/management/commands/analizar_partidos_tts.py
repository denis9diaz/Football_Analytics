from django.core.management.base import BaseCommand
from django.utils.timezone import now
from random import uniform
from django.db.models import Q
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis
from analisis.utils.api import fetch_cuota_casa

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
            liga_actual = partido.liga
            temporada_actual = partido.fecha.year
            temporadas_validas = [temporada_actual - i for i in range(3)]

            def calcular_prob_marcar(equipo, contexto, fecha_limite):
                filtros_comunes = {
                    'fecha__lt': fecha_limite,
                    'liga': liga_actual,
                    'fecha__year__in': temporadas_validas,
                }

                if contexto == 'local':
                    partidos = Partido.objects.filter(
                        equipo_local=equipo,
                        marco_local__isnull=False,
                        **filtros_comunes
                    ).order_by('-fecha')
                    campo = 'marco_local'
                elif contexto == 'visitante':
                    partidos = Partido.objects.filter(
                        equipo_visitante=equipo,
                        marco_visitante__isnull=False,
                        **filtros_comunes
                    ).order_by('-fecha')
                    campo = 'marco_visitante'
                elif contexto == 'local_recibe':
                    partidos = Partido.objects.filter(
                        equipo_local=equipo,
                        marco_visitante__isnull=False,
                        **filtros_comunes
                    ).order_by('-fecha')
                    campo = 'marco_visitante'
                elif contexto == 'visitante_recibe':
                    partidos = Partido.objects.filter(
                        equipo_visitante=equipo,
                        marco_local__isnull=False,
                        **filtros_comunes
                    ).order_by('-fecha')
                    campo = 'marco_local'
                else:
                    return 0.0

                if not partidos.exists():
                    return 0.0

                cumple = [bool(getattr(p, campo)) for p in partidos]
                total = len(cumple)
                aciertos = sum(cumple)

                if aciertos == 0:
                    return 0.0

                porcentaje = aciertos / total

                if not cumple[0]:
                    racha = next((i for i, ok in enumerate(cumple) if ok), len(cumple))
                    return 1 - ((1 - porcentaje) ** (racha + 1))
                return porcentaje

            # LOCAL MARCA
            if 'local' not in ya_creados:
                prob_local = (
                    calcular_prob_marcar(local, 'local', partido.fecha) +
                    calcular_prob_marcar(visitante, 'visitante_recibe', partido.fecha)
                ) / 2

                cuota_real = round(1 / prob_local, 2) if prob_local > 0 else 99.99

                try:
                    cuota_casa = fetch_cuota_casa(
                        int(partido.codigo_api),
                        "Home Team Score a Goal",
                        "Yes"
                    )
                    if cuota_casa is None:
                        raise ValueError("Cuota no encontrada")
                    valor = round((cuota_casa / cuota_real - 1) * 100, 2)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"{partido} (LOCAL): ❌ Cuota no encontrada - {e}"))
                    cuota_casa = None
                    valor = None

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
                    f"{partido} (LOCAL marca) -> prob: {round(prob_local*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa if cuota_casa is not None else '–'}, valor: {valor if valor is not None else '–'}%"
                ))

            # VISITANTE MARCA
            if 'visitante' not in ya_creados:
                prob_visit = (
                    calcular_prob_marcar(visitante, 'visitante', partido.fecha) +
                    calcular_prob_marcar(local, 'local_recibe', partido.fecha)
                ) / 2

                cuota_real = round(1 / prob_visit, 2) if prob_visit > 0 else 99.99

                try:
                    cuota_casa = fetch_cuota_casa(
                        int(partido.codigo_api),
                        "Away Team Score a Goal",
                        "Yes"
                    )
                    if cuota_casa is None:
                        raise ValueError("Cuota no encontrada")
                    valor = round((cuota_casa / cuota_real - 1) * 100, 2)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"{partido} (VISITANTE): ❌ Cuota no encontrada - {e}"))
                    cuota_casa = None
                    valor = None

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
                    f"{partido} (VISITANTE marca) -> prob: {round(prob_visit*100,2)}%, cuota: {cuota_real}, casa: {cuota_casa if cuota_casa is not None else '–'}, valor: {valor if valor is not None else '–'}%"
                ))
