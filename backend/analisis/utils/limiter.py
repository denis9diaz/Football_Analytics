# backend/analisis/utils/limiter.py
from datetime import datetime, timedelta
from collections import deque
import time

class APIRateLimiter:
    def __init__(self, max_daily=7500, max_per_minute=300):
        self.daily_limit = max_daily
        self.minute_limit = max_per_minute
        self.request_times = deque()
        self.daily_count = 0
        self.day_start = datetime.utcnow()

    def wait_if_needed(self):
        now = datetime.utcnow()

        # Reset día si ha pasado
        if (now - self.day_start).days >= 1:
            self.day_start = now
            self.daily_count = 0
            self.request_times.clear()

        # Limpiar requests viejas del último minuto
        one_minute_ago = now - timedelta(minutes=1)
        while self.request_times and self.request_times[0] < one_minute_ago:
            self.request_times.popleft()

        # Si se excede el límite diario
        if self.daily_count >= self.daily_limit:
            raise Exception("⛔ Límite diario alcanzado: 7500 requests.")

        # Si se excede el límite por minuto, espera
        while len(self.request_times) >= self.minute_limit:
            time.sleep(1)  # espera 1 segundo y revisa de nuevo
            now = datetime.utcnow()
            one_minute_ago = now - timedelta(minutes=1)
            while self.request_times and self.request_times[0] < one_minute_ago:
                self.request_times.popleft()

        # Registrar esta llamada
        self.request_times.append(datetime.utcnow())
        self.daily_count += 1

limiter = APIRateLimiter()
