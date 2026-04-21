from django.db import models

class ExchangeRate(models.Model):
    SOURCE_CHOICES = (
        ('BCV', 'Banco Central de Venezuela'),
        ('PARALELO', 'Dólar Paralelo'),
        ('BINANCE', 'Binance P2P'),
    )
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='BCV', verbose_name="Fuente de la Tasa")
    value = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="Valor de la Tasa")
    fecha_valor = models.DateField(verbose_name="Fecha Valor Oficial", help_text="La fecha dada por la fuente para esta tasa")
    
    currency = models.CharField(max_length=10, default='USD', verbose_name="Moneda", help_text="Ej: USD, EUR, CNY, TRY, RUB")
    
    fetched_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Extracción (Scraping)")
    source_url = models.URLField(blank=True, null=True, verbose_name="URL de Origen")
    is_active = models.BooleanField(default=True, verbose_name="¿Es la tasa activa/actual?")
    
    class Meta:
        verbose_name = "Tasa de Cambio"
        verbose_name_plural = "Tasas de Cambio"
        ordering = ['-fecha_valor', '-fetched_at']
        
        # Avoid saving identical dates from the same source and currency multiple times
        unique_together = ('source', 'currency', 'fecha_valor')

    def __str__(self):
        return f"{self.get_source_display()} - {self.value} {self.currency} to VED ({self.fecha_valor})"

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # El valor debe ser positivo
        if self.value <= 0:
            raise ValidationError({'value': "La tasa de cambio debe ser un valor positivo mayor a cero."})
        
        # Evitar fechas demasiado futuristas (máximo mañana)
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)
        if self.fecha_valor > tomorrow:
            raise ValidationError({'fecha_valor': "No se puede registrar una tasa con fecha posterior a mañana."})

