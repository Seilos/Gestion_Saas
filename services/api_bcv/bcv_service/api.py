from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from typing import Optional, List
from decimal import Decimal
from django.utils import timezone
from .scraper import parse_bcv_rate, parse_binance_p2p
from .models import ExchangeRate
from datetime import datetime, date
from django.core.cache import cache
from functools import wraps

api = NinjaAPI(title="BCV & Exchange Rates API", description="Microservicio de Tasas de Cambio")

# --- RATE LIMITING DECORATOR ---
def rate_limit(max_requests=60, timeout=60):
    """Limita la cantidad de peticiones por IP en un tiempo dado (segundos)"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
            key = f"rate_limit_{func.__name__}_{ip}"
            
            count = cache.get(key, 0)
            if count >= max_requests:
                raise HttpError(429, "Too Many Requests - Has excedido tu límite gratuito de consultas temporales.")
            
            cache.set(key, count + 1, timeout)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


class RateResponse(Schema):
    source: str
    currency: str = "USD"
    value: Decimal
    date_text: Optional[str] = None
    fetched_at: str
    success: bool
    error: Optional[str] = None

class RateHistoryResponse(Schema):
    success: bool
    rates: List[RateResponse] = []
    error: Optional[str] = None


@api.get("/rates/bcv/latest", response=RateResponse, summary="Obtener tasa actual")
@rate_limit(max_requests=30, timeout=60) # 30 peticiones por minuto
def get_latest_bcv_rate(request, currency: str = "USD"):
    today = timezone.now().date()
    currency = currency.upper()
    
    cached_rate = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True, fecha_valor__gte=today).order_by('fecha_valor', '-fetched_at').first()
    if not cached_rate:
         cached_rate = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True, fecha_valor=today).first()

    if cached_rate and cached_rate.fecha_valor >= today:
        return {
            "source": "BCV",
            "currency": cached_rate.currency,
            "value": cached_rate.value,
            "date_text": f"Caché de BD ({cached_rate.fecha_valor})",
            "fetched_at": cached_rate.fetched_at.isoformat(),
            "success": True
        }

    result = parse_bcv_rate()
    if result.get("success"):
        date_iso = result.get("date_iso")
        fecha_valor_dt = today
        if date_iso:
            try:
                fecha_valor_dt = datetime.strptime(date_iso, "%Y-%m-%d").date()
            except ValueError:
                pass

        saved_requested_rate = None
        for rate_data in result.get("rates", []):
            try:
                obj, created = ExchangeRate.objects.get_or_create(
                    source="BCV",
                    currency=rate_data["currency"],
                    fecha_valor=fecha_valor_dt,
                    defaults={
                        "value": rate_data["value"],
                        "source_url": "https://www.bcv.org.ve/"
                    }
                )
                if obj.currency == currency:
                    saved_requested_rate = obj
            except Exception as e:
                pass 
                
        if saved_requested_rate:
             return {
                "source": "BCV",
                "currency": saved_requested_rate.currency,
                "value": saved_requested_rate.value,
                "date_text": result.get("date_text"),
                "fetched_at": timezone.now().isoformat(),
                "success": True
             }
        else:
             fallback_rate = next((r for r in result.get("rates", []) if r["currency"] == currency), None)
             if fallback_rate:
                  return {**fallback_rate, "date_text": result.get("date_text"), "fetched_at": timezone.now().isoformat()}
                  
    last_rate = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    if last_rate:
        return {
            "source": "BCV",
            "currency": last_rate.currency,
            "value": last_rate.value,
            "date_text": "Caché de BD Histórico (Web Caída)",
            "fetched_at": last_rate.fetched_at.isoformat(),
            "success": True
        }

    return {"success": False, "source": "BCV", "error": result.get("error", "Error desconocido"), "value": 0, "fetched_at": timezone.now().isoformat()}


@api.get("/rates/bcv/history", response=RateHistoryResponse, summary="Obtener historial de tasas")
@rate_limit(max_requests=10, timeout=60) # Más restrictivo para evitar abuso de DB
def get_bcv_history(request, from_date: Optional[date] = None, to_date: Optional[date] = None, currency: str = "USD"):
    currency = currency.upper()
    qs = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True)
    
    if from_date:
        qs = qs.filter(fecha_valor__gte=from_date)
    if to_date:
         qs = qs.filter(fecha_valor__lte=to_date)
    
    # Limitar a máximo 30 días para evitar payloads gigantes
    qs = qs.order_by('-fecha_valor')[:30]
    
    results = []
    for r in qs:
        results.append({
             "source": r.source,
             "currency": r.currency,
             "value": r.value,
             "date_text": f"Histórico del {r.fecha_valor}",
             "fetched_at": r.fetched_at.isoformat(),
             "success": True
        })
    return {"success": True, "rates": results}


@api.get("/rates/binance/latest", response=RateResponse, summary="Obtener tasa USDT Binance P2P")
@rate_limit(max_requests=30, timeout=60)
def get_latest_binance_rate(request):
    today = timezone.now().date()
    
    cached_rate = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True, fecha_valor=today).order_by('-fetched_at').first()
    
    # Binance cambia constantemente, así que el caché aquí debería ser corto (minutos).
    # Para simplificar, si se trajo hoy hace menos de 10 minutos, lo devolvemos
    if cached_rate and (timezone.now() - cached_rate.fetched_at).total_seconds() < 600:
        return {
            "source": "BINANCE",
            "currency": "USDT",
            "value": cached_rate.value,
            "date_text": f"Caché Corto (Binance P2P)",
            "fetched_at": cached_rate.fetched_at.isoformat(),
            "success": True
        }

    result = parse_binance_p2p()
    if result.get("success"):
        try:
            ExchangeRate.objects.create(
                source="BINANCE",
                currency="USDT",
                value=result["value"],
                fecha_valor=today,
                source_url="https://p2p.binance.com/"
            )
        except Exception:
            pass
            
        return {
            **result,
            "fetched_at": timezone.now().isoformat()
        }
        
    last_rate = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    if last_rate:
        return {
            "source": "BINANCE",
            "currency": "USDT",
            "value": last_rate.value,
            "date_text": "Caché Histórico",
            "fetched_at": last_rate.fetched_at.isoformat(),
            "success": True
        }

    return {"success": False, "source": "BINANCE", "error": result.get("error", "Error desconocido"), "value": 0, "fetched_at": timezone.now().isoformat()}

