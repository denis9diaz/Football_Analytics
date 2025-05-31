# Ejecutar todos los comandos de análisis desde PowerShell
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
