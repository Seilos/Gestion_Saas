from django.shortcuts import render
from django.utils import timezone
from bcv_service.models import ExchangeRate

def home_view(request):
    """Vista principal para el dashboard de DaaS."""
    today = timezone.now().date()
    
    # Obtenemos la última tasa en caché de cada una de las principales
    # Para USD de BCV
    bcv_usd = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    # Para EUR de BCV
    bcv_eur = ExchangeRate.objects.filter(source="BCV", currency="EUR", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    # Para Binance USDT
    binance_usdt = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    
    context = {
        'bcv_usd': bcv_usd,
        'bcv_eur': bcv_eur,
        'binance_usdt': binance_usdt,
        'last_update': timezone.now()
    }
    return render(request, 'index.html', context)
