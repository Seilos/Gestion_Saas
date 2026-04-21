import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import datetime
from bcv_service.scraper import parse_bcv_rate, parse_binance_p2p
from bcv_service.models import ExchangeRate

logger = logging.getLogger(__name__)

def update_bcv_rates():
    """Función que ejecuta el scraper del BCV en segundo plano y guarda en BD"""
    logger.info("Iniciando tarea programada: Actualización BCV...")
    result = parse_bcv_rate()
    today = timezone.now().date()
    
    if result.get("success"):
        date_iso = result.get("date_iso")
        fecha_valor_dt = today
        if date_iso:
            try:
                fecha_valor_dt = datetime.strptime(date_iso, "%Y-%m-%d").date()
            except ValueError:
                pass

        for rate_data in result.get("rates", []):
            try:
                ExchangeRate.objects.get_or_create(
                    source="BCV",
                    currency=rate_data["currency"],
                    fecha_valor=fecha_valor_dt,
                    defaults={
                        "value": rate_data["value"],
                        "source_url": "https://www.bcv.org.ve/"
                    }
                )
            except Exception as e:
                logger.error(f"Error guardando tasa programada BCV {rate_data['currency']}: {e}")
        logger.info("Actualización BCV exitosa.")
    else:
        logger.error(f"Error en tarea BCV: {result.get('error')}")

def update_binance_rates():
    """Función que ejecuta el scraper de Binance en segundo plano y guarda en BD"""
    logger.info("Iniciando tarea programada: Actualización Binance P2P...")
    result = parse_binance_p2p()
    today = timezone.now().date()
    
    if result.get("success"):
        try:
            ExchangeRate.objects.create(
                source="BINANCE",
                currency="USDT",
                value=result["value"],
                fecha_valor=today,
                source_url="https://p2p.binance.com/"
            )
            logger.info("Actualización Binance exitosa.")
        except Exception as e:
            logger.error(f"Error guardando tasa programada Binance: {e}")
    else:
        logger.error(f"Error en tarea Binance: {result.get('error')}")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Caracas")
    
    # Binance se actualiza cada 15 minutos siempre
    scheduler.add_job(update_binance_rates, 'interval', minutes=15, id='binance_job', replace_existing=True)
    
    # BCV se actualiza cada 30 minutos (suficiente para captar cuando lo actualicen alrededor de las 3pm)
    # y así evitamos golpear el BCV tan seguido.
    scheduler.add_job(update_bcv_rates, 'interval', minutes=30, id='bcv_job', replace_existing=True)
    
    scheduler.start()
    logger.info("Scheduler de tasas en segundo plano iniciado.")
