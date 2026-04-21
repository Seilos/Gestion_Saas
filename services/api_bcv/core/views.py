from django.shortcuts import render
from django.utils import timezone
import json
from bcv_service.models import ExchangeRate

from django.db.models import Avg

from django.db.models import Avg, Q
from datetime import timedelta

def home_view(request):
    """Vista Nexo 21 con filtros de tiempo avanzados para el historial."""
    today = timezone.now().date()
    
    bcv_usd = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    bcv_eur = ExchangeRate.objects.filter(source="BCV", currency="EUR", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    binance_usdt = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    
    # --- FILTROS DE HISTORIAL ---
    selected_currency = request.GET.get('currency', 'USD').upper()
    period = request.GET.get('period', 'month') # Default: Mes actual
    available_currencies = ExchangeRate.objects.order_by('currency').values_list('currency', flat=True).distinct()
    
    history_qs_table = ExchangeRate.objects.filter(currency=selected_currency).order_by('-fecha_valor', '-fetched_at')
    
    if period == 'month':
        history_qs_table = history_qs_table.filter(fecha_valor__month=today.month, fecha_valor__year=today.year)
    elif period == '3months':
        three_months_ago = today - timedelta(days=90)
        history_qs_table = history_qs_table.filter(fecha_valor__gte=three_months_ago)
    elif period == 'year':
        history_qs_table = history_qs_table.filter(fecha_valor__year=today.year)
    # Si es 'all', no filtramos más.

    history_table = history_qs_table[:250] # Aumentamos el límite para ver más historial
    
    # --- GRÁFICA COMPARATIVA ---
    history_qs_chart = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor')[:15]
    chart_labels = []
    chart_data_bcv = []
    chart_data_binance = []
    
    for r in reversed(history_qs_chart):
        dia = r.fecha_valor
        chart_labels.append(dia.strftime("%d/%m"))
        chart_data_bcv.append(float(r.value))
        avg_binance = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", fecha_valor=dia).aggregate(Avg('value'))['value__avg']
        chart_data_binance.append(float(avg_binance) if avg_binance else None)
        
    context = {
        'bcv_usd': bcv_usd,
        'bcv_eur': bcv_eur,
        'binance_usdt': binance_usdt,
        'selected_currency': selected_currency,
        'period': period,
        'available_currencies': available_currencies,
        'history_table': history_table,
        'last_update': timezone.now(),
        'chart_labels': json.dumps(chart_labels),
        'chart_data_bcv': json.dumps(chart_data_bcv),
        'chart_data_binance': json.dumps(chart_data_binance)
    }
    return render(request, 'index.html', context)
