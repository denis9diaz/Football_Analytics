from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q
from random import uniform
from analisis.models import Partido, PartidoAnalisis, MetodoAnalisis
from analisis.utils.api_odds import fetch_cuota_casa

class Command(BaseCommand):
    help = 'Analiza partidos del día para el método Over 2.5 Goles'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        metodo = MetodoAnalisis.objects.get(nombre__iexact='Over 2.5')

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

            def calcular_prob(equipo, fecha_limite):
                historial = Partido.objects.filter(
                    Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
                    goles_local_ft__isnull=False,
                    goles_visitante_ft__isnull=False,
                    fecha__lt=fecha_limite,
                    liga=liga_actual,
                    fecha__year__in=temporadas_validas,
                ).order_by('-fecha')

                if not historial.exists():
                    return 0.0

                cumple = [
                    (p.goles_local_ft + p.goles_visitante_ft) > 2
                    for p in historial
                ]

                total = len(cumple)
                aciertos = sum(cumple)

                if aciertos == 0:
                    return 0.0

                porcentaje = aciertos / total

                if not cumple[0]:
                    racha = next((i for i, ok in enumerate(cumple) if ok), len(cumple))
                    return 1 - ((1 - porcentaje) ** (racha + 1))
                return porcentaje

            prob_local = calcular_prob(local, partido.fecha)
            prob_visit = calcular_prob(visitante, partido.fecha)
            prob_media = (prob_local + prob_visit) / 2

            cuota_real = round(1 / prob_media, 2) if prob_media > 0 else 99.99

            try:
                cuota_casa = fetch_cuota_casa(int(partido.codigo_api), "Goals Over/Under", "Over 2.5")
                if cuota_casa is None:
                    raise ValueError("Cuota no encontrada")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"{partido}: ❌ Cuota no encontrada - {e}"))
                cuota_casa = round(max(cuota_real + uniform(-0.3, 0.3), 1.00), 2)
                mostrar_cuota = "–"
                mostrar_valor = "–"
                valor = None
            else:
                mostrar_cuota = cuota_casa
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
                f"{partido} -> Over 2.5: {round(prob_media*100,2)}%, cuota: {cuota_real}, casa: {mostrar_cuota}, valor: {mostrar_valor}"
            ))
