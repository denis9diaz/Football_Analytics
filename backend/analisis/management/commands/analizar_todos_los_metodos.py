from django.core.management.base import BaseCommand
import subprocess
import sys

COMANDOS = [
    "analizar_partidos_btts",
    "analizar_partidos_golht",
    "analizar_partidos_home_win",
    "analizar_partidos_over1_5_home",
    "analizar_partidos_over1_5",
    "analizar_partidos_over2_5",
    "analizar_partidos_tts",
]

class Command(BaseCommand):
    help = 'Ejecuta en orden todos los comandos de análisis de métodos disponibles'

    def handle(self, *args, **kwargs):
        for comando in COMANDOS:
            self.stdout.write(self.style.NOTICE(f"\n⏳ Ejecutando {comando}..."))
            result = subprocess.run([sys.executable, "manage.py", comando], capture_output=True, text=True)

            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f"✅ {comando} completado con éxito.\n"))
                self.stdout.write(result.stdout)
            else:
                self.stdout.write(self.style.ERROR(f"❌ Error al ejecutar {comando}"))
                self.stdout.write(result.stderr)
