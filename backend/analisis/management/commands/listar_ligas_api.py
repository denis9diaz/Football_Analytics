from django.core.management.base import BaseCommand
import requests
import os
from dotenv import load_dotenv
from analisis.utils.limiter import APIRateLimiter

load_dotenv()

API_URL = os.getenv("RAPIDAPI_URL")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

limiter = APIRateLimiter()

class Command(BaseCommand):
    help = "Muestra todas las ligas disponibles en API-FOOTBALL"

    def handle(self, *args, **kwargs):
        limiter.wait_if_needed()
        url = f"{API_URL}/leagues"
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": API_HOST,
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code != 200:
            self.stderr.write(f"❌ Error: {response.status_code} - {response.text}")
            return

        ligas = data["response"]
        self.stdout.write(f"🔎 {len(ligas)} ligas encontradas:\n")

        for item in ligas:
            league = item["league"]
            country = item["country"]
            self.stdout.write(
                f"ID: {league['id']} | {league['name']} ({country['name']}) | Tipo: {league['type']}"
            )
