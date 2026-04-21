from django.shortcuts import render
from django.utils import timezone
import json
from bcv_service.models import ExchangeRate

def home_view(request):
    """Vista principal para el portal Nexo 21 - Monitor de Divisas."""
    today = timezone.now().date()
    
    # Monedas para las tarjetas principales
    bcv_usd = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    bcv_eur = ExchangeRate.objects.filter(source="BCV", currency="EUR", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    binance_usdt = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    
    # Filtro de moneda para el historial (vía GET)
    selected_currency = request.GET.get('currency', 'USD').upper()
    available_currencies = ExchangeRate.objects.order_by('currency').values_list('currency', flat=True).distinct()
    
    # Datos para la Tabla de Historial
    history_table = ExchangeRate.objects.filter(currency=selected_currency).order_by('-fecha_valor', '-fetched_at')[:20]
    
    # Datos para la Gráfica (BCV USD por defecto)
    history_qs = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor')[:15]
    chart_labels = []
    chart_data = []
    for r in reversed(history_qs):
        chart_labels.append(r.fecha_valor.strftime("%d/%m"))
        chart_data.append(float(r.value))
        
    context = {
        'bcv_usd': bcv_usd,
        'bcv_eur': bcv_eur,
        'binance_usdt': binance_usdt,
        'selected_currency': selected_currency,
        'available_currencies': available_currencies,
        'history_table': history_table,
        'last_update': timezone.now(),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'index.html', context)
