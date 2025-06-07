import os
import requests
from dotenv import load_dotenv
from analisis.utils.limiter import APIRateLimiter

load_dotenv()

API_URL = os.getenv("RAPIDAPI_URL")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

limiter = APIRateLimiter()

def fetch_fixture_por_id(fixture_id: str) -> dict:
    """
    Consulta un fixture individual por su ID (codigo_api).
    """
    limiter.wait_if_needed()

    url = f"{API_URL}/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {
        "id": fixture_id
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"❌ Error al obtener fixture {fixture_id}: {response.status_code}")
        return {}

    return response.json()
