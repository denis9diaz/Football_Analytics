# Este archivo contiene los comandos para gestionar tu análisis de partidos y rachas.

# 1. Ejecutar todos los comandos de análisis
$comandos = @(
  "analizar_partidos_btts",
  "analizar_partidos_golht",
  "analizar_partidos_home_win",
  "analizar_partidos_over1_5_home",
  "analizar_partidos_over1_5",
  "analizar_partidos_over2_5",
  "analizar_partidos_tts"
)

foreach ($c in $comandos) {
  Write-Host "`n⏳ Ejecutando $c..."
  python manage.py $c
}

# 2. Ejecutar comando para recalcular todas las rachas
Write-Host "`n⏳ Ejecutando recalcular_rachas..."
python manage.py recalcular_rachas


<#
-------------------------------------------------------------------------------
# 3. Código para usar dentro del shell de Django para listar partidos del Real Madrid

from analisis.models import Partido, Equipo
from django.db.models import Q

rm = Equipo.objects.get(nombre='Real Madrid')
partidos = Partido.objects.filter(Q(equipo_local=rm) | Q(equipo_visitante=rm)).order_by('fecha')
for p in partidos:
    local = p.equipo_local.nombre if p.equipo_local else 'Desconocido'
    visitante = p.equipo_visitante.nombre if p.equipo_visitante else 'Desconocido'
    fecha = p.fecha.strftime('%Y-%m-%d %H:%M')
    print(f"📅 {fecha} | {local} vs {visitante}")
    print(f"    Goles HT: {p.goles_local_ht} - {p.goles_visitante_ht} | FT: {p.goles_local_ft} - {p.goles_visitante_ft}")
    print(f"    GOL HT: {p.gol_ht} | TTS Local: {p.goles_local_ft > 0 if p.goles_local_ft is not None else 'N/A'}, Visitante: {p.goles_visitante_ft > 0 if p.goles_visitante_ft is not None else 'N/A'} | BTTS: {p.btts}")
    print(f"    Over 1.5: {p.over_1_5} | Over 2.5: {p.over_2_5}")
    print(f"    Resultado 1X2: {p.resultado_1x2}")
    print()

-------------------------------------------------------------------------------
# 4. Código para usar dentro del shell de Django para listar rachas del Real Madrid

from analisis.models import RachaEquipo, Equipo

rm = Equipo.objects.get(nombre='Real Madrid')
rachas = RachaEquipo.objects.filter(equipo=rm).order_by('condicion', 'contexto', 'tipo')
for r in rachas:
    print(f'🔹 {r.condicion.upper()} | {r.contexto.upper()} | {r.tipo.upper()} ➜ {r.cantidad}')

-------------------------------------------------------------------------------
#>
