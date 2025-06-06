from django.utils.timezone import now
from analisis.models import Equipo, RachaEquipo, Partido
from django.db.models import Q

CONDICIONES = {
    'gol_ht': lambda p, e: p.gol_ht,
    'tts': lambda p, e: p.marco_local if p.equipo_local == e else p.marco_visitante,
    'over_1_5': lambda p, e: p.over_1_5,
    'over_2_5': lambda p, e: p.over_2_5,
    'over_1_5_local': lambda p, e: p.over_1_5_local,
    'btts': lambda p, e: p.btts,
    'ganar': lambda p, e: (
        (p.goles_local_ft > p.goles_visitante_ft and p.equipo_local == e) or
        (p.goles_visitante_ft > p.goles_local_ft and p.equipo_visitante == e)
    ),
    'over_1_5_marcados': lambda p, e: (
        p.goles_local_ft >= 2 if p.equipo_local == e else p.goles_visitante_ft >= 2
    ),
    'over_1_5_recibidos': lambda p, e: (
        p.goles_visitante_ft >= 2 if p.equipo_local == e else p.goles_local_ft >= 2
    ),
}

CONTEXTOS = ['local', 'visitante', 'ambos']

def actualizar_rachas_historicas():
    año_actual = now().year
    años_validos = [año_actual, año_actual - 1, año_actual - 2]

    for equipo in Equipo.objects.all():
        for liga in equipo.ligas.all():
            for condicion, func in CONDICIONES.items():
                for contexto in CONTEXTOS:
                    partidos = Partido.objects.filter(
                        liga=liga,
                        fecha__lt=now(),
                        goles_local_ft__isnull=False,
                        goles_visitante_ft__isnull=False,
                        fecha__year__in=años_validos
                    ).filter(
                        Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
                    ).order_by('fecha')

                    if contexto == 'local':
                        partidos = partidos.filter(equipo_local=equipo)
                    elif contexto == 'visitante':
                        partidos = partidos.filter(equipo_visitante=equipo)

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
                        liga=liga,
                        defaults={'cantidad': racha_max}
                    )
