import os
import requests
from dotenv import load_dotenv
from analisis.utils.limiter import APIRateLimiter

load_dotenv()

API_URL = os.getenv("RAPIDAPI_URL")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

limiter = APIRateLimiter()

def fetch_fixtures_futuros(liga_id: int, temporada: str) -> dict:
    """
    Llama a la API-Football para obtener partidos FUTUROS (sin resultado aún)
    de una liga y temporada concreta.
    """
    limiter.wait_if_needed()

    url = f"{API_URL}/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {
        "league": liga_id,
        "season": temporada,
        "status": "NS"  # Not Started
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    return response.json()
