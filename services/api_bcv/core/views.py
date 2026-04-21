from django.shortcuts import render
from django.utils import timezone
import json
from bcv_service.models import ExchangeRate

from django.db.models import Avg

def home_view(request):
    """Vista principal Nexo 21 Dólar Venezuela con Publicidad y Gráfica Comparativa."""
    today = timezone.now().date()
    
    bcv_usd = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    bcv_eur = ExchangeRate.objects.filter(source="BCV", currency="EUR", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    binance_usdt = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    
    selected_currency = request.GET.get('currency', 'USD').upper()
    available_currencies = ExchangeRate.objects.order_by('currency').values_list('currency', flat=True).distinct()
    history_table = ExchangeRate.objects.filter(currency=selected_currency).order_by('-fecha_valor', '-fetched_at')[:20]
    
    # --- LÓGICA DE GRÁFICA COMPARATIVA (Últimos 15 días) ---
    history_qs = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor')[:15]
    chart_labels = []
    chart_data_bcv = []
    chart_data_binance = []
    
    # Recorremos los últimos 15 días para buscar promedios
    for r in reversed(history_qs):
        dia = r.fecha_valor
        chart_labels.append(dia.strftime("%d/%m"))
        chart_data_bcv.append(float(r.value))
        
        # Promedio de Binance para ese mismo día específico
        avg_binance = ExchangeRate.objects.filter(
            source="BINANCE", 
            currency="USDT", 
            fecha_valor=dia
        ).aggregate(Avg('value'))['value__avg']
        
        # Si no hubo records ese día (ej. día nuevo), usamos el último conocido o 0
        chart_data_binance.append(float(avg_binance) if avg_binance else None)
        
    context = {
        'bcv_usd': bcv_usd,
        'bcv_eur': bcv_eur,
        'binance_usdt': binance_usdt,
        'selected_currency': selected_currency,
        'available_currencies': available_currencies,
        'history_table': history_table,
        'last_update': timezone.now(),
        'chart_labels': json.dumps(chart_labels),
        'chart_data_bcv': json.dumps(chart_data_bcv),
        'chart_data_binance': json.dumps(chart_data_binance)
    }
    return render(request, 'index.html', context)
