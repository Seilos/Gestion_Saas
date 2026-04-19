from ninja import NinjaAPI, Schema
from typing import Optional
from decimal import Decimal
from django.utils import timezone
from .scraper import parse_bcv_rate
from .models import ExchangeRate
from datetime import datetime

api = NinjaAPI(title="BCV & Exchange Rates API", description="Microservicio de Tasas de Cambio")

class RateResponse(Schema):
    source: str
    value: Decimal
    date_text: Optional[str] = None
    fetched_at: str
    success: bool
    error: Optional[str] = None

@api.get("/rates/bcv/latest", response=RateResponse)
def get_latest_bcv_rate(request):
    """
    Obtiene la última tasa del BCV en tiempo real.
    Si ya se escrapeó en la última hora, puede devolver desde la caché de la BD (para futuro).
    Por ahora, extrae directamente de la web o de la BD si la web falla.
    """
    # Intentar obtener de la web
    result = parse_bcv_rate()
    
    if result.get("success"):
        # Guardar en Base de Datos de manera "Fire & Forget"
        # Esto sirve para ir alimentando el historial de dolarvzla
        # TODO: Implementar lógica para evitar duplicados si la fecha es la misma
        try:
            ExchangeRate.objects.create(
                source="BCV",
                value=result["value"],
                fecha_valor=timezone.now().date(), # TODO: Parse date_text correctamente
                source_url="https://www.bcv.org.ve/"
            )
        except Exception as e:
            pass # No queremos romper el flujo si la DB falla al guardar
            
        return {
            **result,
            "fetched_at": timezone.now().isoformat()
        }
    else:
        # Fallback: intentar buscar el último valor guardado en la BD
        last_rate = ExchangeRate.objects.filter(source="BCV", is_active=True).order_by('-fetched_at').first()
        if last_rate:
            return {
                "source": "BCV",
                "value": last_rate.value,
                "date_text": "Caché de Base de Datos (Web Caída)",
                "fetched_at": last_rate.fetched_at.isoformat(),
                "success": True
            }
            
        return result # Devuelve el error al final

