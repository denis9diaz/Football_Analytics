import os
import requests
from dotenv import load_dotenv
from analisis.utils.limiter import APIRateLimiter

load_dotenv()

API_URL = os.getenv("RAPIDAPI_URL")
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

limiter = APIRateLimiter()

def fetch_cuota_casa(fixture_id: int, mercado: str, valor_objetivo: str, casa: str = "Bet365") -> float | None:
    """
    Busca la cuota primero en la casa seleccionada (por defecto Bet365), y si no la encuentra,
    la busca en cualquier otra casa disponible.
    """
    limiter.wait_if_needed()

    url = f"{API_URL}/odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    params = {
        "fixture": fixture_id
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    data = response.json().get("response", [])

    # Paso 1: Buscar en la casa principal (Bet365 por defecto)
    for entrada in data:
        for bookmaker in entrada.get("bookmakers", []):
            if bookmaker["name"] == casa:
                for market in bookmaker.get("bets", []):
                    if market["name"] == mercado:
                        for valor in market.get("values", []):
                            if valor["value"].strip().lower() == valor_objetivo.strip().lower():
                                try:
                                    return float(valor["odd"])
                                except (ValueError, TypeError):
                                    continue

    # Paso 2: Buscar en cualquier otra casa si no se encontró en la principal
    for entrada in data:
        for bookmaker in entrada.get("bookmakers", []):
            for market in bookmaker.get("bets", []):
                if market["name"] == mercado:
                    for valor in market.get("values", []):
                        if valor["value"].strip().lower() == valor_objetivo.strip().lower():
                            try:
                                return float(valor["odd"])
                            except (ValueError, TypeError):
                                continue

    return None
