from django.core.management.base import BaseCommand
from analisis.models import Liga, Equipo

class Command(BaseCommand):
    help = "Crea los equipos actualizados para las principales ligas europeas"

    equipos_por_liga = {
        "LaLiga": [
            "Barcelona", "Real Madrid", "Atlético de Madrid", "Athletic Club", "Villarreal",
            "Real Betis", "Celta de Vigo", "Rayo Vallecano", "Osasuna", "Mallorca",
            "Real Sociedad", "Valencia", "Getafe", "Espanyol", "Alavés",
            "Girona", "Sevilla", "Leganés", "Las Palmas", "Real Valladolid"
        ],
        "Premier League": [
            "Liverpool", "Arsenal", "Manchester City", "Chelsea", "Newcastle",
            "Aston Villa", "Nottingham Forest", "Brighton", "Bournemouth", "Brentford",
            "Fulham", "Crystal Palace", "Everton", "West Ham", "Manchester Utd",
            "Wolves", "Tottenham", "Leicester", "Ipswich", "Southampton"
        ],
        "Serie A": [
            "Nápoles", "Inter", "Atalanta", "Juventus", "Roma",
            "Fiorentina", "Lazio", "AC Milan", "Bolonia", "Como",
            "Torino", "Udinese", "Genoa", "Verona", "Cagliari",
            "Parma", "Lecce", "Empoli", "Venezia", "Monza"
        ],
        "Bundesliga": [
            "Bayern Múnich", "Bayer Leverkusen", "Eintracht Frankfurt", "Borussia Dortmund", "Friburgo",
            "Mainz", "RB Leipzig", "Werder Bremen", "Stuttgart", "Borussia M'gladbach",
            "Wolfsburgo", "Augsburgo", "Union Berlin", "St. Pauli", "Hoffenheim",
            "Heidenheim", "Kiel", "Bochum"
        ],
        "Ligue 1": [
            "PSG", "Marsella", "Mónaco", "Niza", "Lille",
            "Lyon", "Estrasburgo", "Lens", "Brest", "Toulouse",
            "Auxerre", "Stade Rennais", "Nantes", "Angers", "Le Havre",
            "Reims", "Saint-Étienne", "Montpellier"
        ]
    }

    def handle(self, *args, **kwargs):
        for nombre_liga, equipos in self.equipos_por_liga.items():
            try:
                liga = Liga.objects.get(nombre=nombre_liga)
            except Liga.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ No se encontró la liga '{nombre_liga}'"))
                continue

            for nombre_equipo in equipos:
                equipo, creado = Equipo.objects.get_or_create(nombre=nombre_equipo, liga=liga)
                if creado:
                    self.stdout.write(self.style.SUCCESS(f"✅ Creado: {nombre_equipo} en {nombre_liga}"))
                else:
                    self.stdout.write(f"⚠️ Ya existía: {nombre_equipo} en {nombre_liga}")
