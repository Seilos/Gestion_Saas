import os
import django
import sys
from datetime import date, timedelta
from decimal import Decimal

# Configurar entorno Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from bcv_service.models import ExchangeRate

def seed_data():
    print("Iniciando carga de datos históricos...")
    
    # Datos aproximados de las últimas semanas para USD y EUR (BCV)
    # Nota: Estos son valores de referencia para que la gráfica nazca con vida.
    history_usd = [
        (date(2026, 4, 20), 481.22), (date(2026, 4, 19), 480.10), (date(2026, 4, 18), 480.10),
        (date(2026, 4, 17), 478.50), (date(2026, 4, 16), 476.20), (date(2026, 4, 15), 474.15),
        (date(2026, 4, 14), 473.00), (date(2026, 4, 13), 472.10), (date(2026, 4, 12), 470.50),
        (date(2026, 4, 11), 470.50), (date(2026, 4, 10), 469.80), (date(2026, 4, 9), 468.20),
        (date(2026, 4, 8), 465.10), (date(2026, 4, 7), 464.00), (date(2026, 4, 6), 462.15),
    ]

    history_eur = [
        (date(2026, 4, 20), 512.44), (date(2026, 4, 19), 511.20), (date(2026, 4, 18), 511.20),
        (date(2026, 4, 17), 509.80), (date(2026, 4, 16), 508.50), (date(2026, 4, 15), 506.10),
        (date(2026, 4, 14), 505.00), (date(2026, 4, 13), 504.15), (date(2026, 4, 12), 502.80),
        (date(2026, 4, 11), 502.80), (date(2026, 4, 10), 501.20), (date(2026, 4, 9), 499.50),
    ]

    # Binance (Tasa paralela un poco por encima)
    history_binance = [
        (date(2026, 4, 20), 515.20), (date(2026, 4, 19), 512.10), (date(2026, 4, 18), 512.10),
        (date(2026, 4, 17), 508.50), (date(2026, 4, 16), 505.20), (date(2026, 4, 15), 503.15),
        (date(2026, 4, 14), 501.00), (date(2026, 4, 13), 500.20), (date(2026, 4, 12), 498.50),
    ]

    total_created = 0

    # Inyectar USD
    for fecha, valor in history_usd:
        obj, created = ExchangeRate.objects.get_or_create(
            source="BCV", currency="USD", fecha_valor=fecha,
            defaults={'value': Decimal(str(valor)), 'source_url': 'https://www.bcv.org.ve/'}
        )
        if created: total_created += 1

    # Inyectar EUR
    for fecha, valor in history_eur:
        obj, created = ExchangeRate.objects.get_or_create(
            source="BCV", currency="EUR", fecha_valor=fecha,
            defaults={'value': Decimal(str(valor)), 'source_url': 'https://www.bcv.org.ve/'}
        )
        if created: total_created += 1

    # Inyectar Binance
    for fecha, valor in history_binance:
        obj, created = ExchangeRate.objects.get_or_create(
            source="BINANCE", currency="USDT", fecha_valor=fecha,
            defaults={'value': Decimal(str(valor)), 'source_url': 'https://p2p.binance.com/'}
        )
        if created: total_created += 1

    print(f"Éxito: Se inyectaron {total_created} registros nuevos.")

if __name__ == "__main__":
    seed_data()
