from django.utils.timezone import now
from analisis.models import Equipo, RachaEquipo, Partido
from django.db.models import Q

CONDICIONES = {
    'gol_ht': lambda p, e: p.gol_ht,
    'tts': lambda p, e: p.marco_local if p.equipo_local == e else p.marco_visitante,
    'over_1_5': lambda p, e: p.over_1_5,
    'over_2_5': lambda p, e: p.over_2_5,
    'over_1_5_local': lambda p, e: p.over_1_5_local,
}

CONTEXTOS = ['local', 'visitante', 'ambos']

def actualizar_rachas():
    for equipo in Equipo.objects.all():
        for condicion, func in CONDICIONES.items():
            for contexto in CONTEXTOS:
                # Filtrar partidos según el contexto
                partidos = Partido.objects.filter(
                    Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
                    fecha__lt=now(),
                    goles_local_ft__isnull=False,
                    goles_visitante_ft__isnull=False
                ).order_by('fecha')

                if contexto == 'local':
                    partidos = partidos.filter(equipo_local=equipo)
                elif contexto == 'visitante':
                    partidos = partidos.filter(equipo_visitante=equipo)

                # Calcular racha actual
                racha_actual = 0
                for p in partidos:
                    if func(p, equipo):
                        racha_actual = 0
                    else:
                        racha_actual += 1

                RachaEquipo.objects.update_or_create(
                    equipo=equipo,
                    condicion=condicion,
                    contexto=contexto,
                    tipo='actual',
                    defaults={'cantidad': racha_actual}
                )

                # Calcular racha histórica
                racha_max = 0
                racha_temp = 0
                for p in partidos:
                    if func(p, equipo):
                        racha_temp = 0
                    else:
                        racha_temp += 1
                        racha_max = max(racha_max, racha_temp)

                RachaEquipo.objects.update_or_create(
                    equipo=equipo,
                    condicion=condicion,
                    contexto=contexto,
                    tipo='historica',
                    defaults={'cantidad': racha_max}
                )
from analisis.utils.actualizar_rachas import actualizar_rachas
actualizar_rachas()
