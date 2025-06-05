import os
import requests
from dotenv import load_dotenv
from analisis.utils.limiter import APIRateLimiter

load_dotenv()

API_URL = os.getenv("RAPIDAPI_URL")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

limiter = APIRateLimiter()


def fetch_fixtures(league_id: int, season: str):
    """
    Llama al endpoint /fixtures de API-Football vía RapidAPI,
    para una liga y temporada concretas (todos los partidos).
    """
    limiter.wait_if_needed()

    url = f"{API_URL}/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {
        "league": league_id,
        "season": season
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    return response.json()


def fetch_fixtures_futuros(league_id: int, season: str):
    """
    Llama al endpoint /fixtures para obtener solo partidos futuros (status=NS).
    """
    limiter.wait_if_needed()

    url = f"{API_URL}/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {
        "league": league_id,
        "season": season,
        "status": "NS"  # Not Started
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    return response.json()

