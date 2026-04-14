import uuid
from django.db import models
from django.conf import settings
from app_saas_auth.models import Organization

class BaseModel(models.Model):
    """
    Motor de Auditoría y Sincronización Local-First.
    Garantiza que nada se borre físicamente y todo sea rastreable.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # --- Auditoría de Creación ---
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="%(class)s_created"
    )

    # --- Auditoría de Actualización ---
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="%(class)s_updated"
    )

    # --- Soft Delete (Borrado Lógico) ---
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="%(class)s_deleted"
    )

    # --- Estado de Activación (Pausa) ---
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="%(class)s_deactivated"
    )

    class Meta:
        abstract = True

class SaaSProduct(BaseModel):
    """
    REGISTRO DE PRODUCTOS:
    Aquí daremos de alta tus herramientas: 'Clara Library', 'BCV API', 'ERP', etc.
    """
    name = models.CharField(max_length=150, verbose_name="Nombre del Producto")
    slug = models.SlugField(unique=True, help_text="Identificador único (ej: clara-library)")
    description = models.TextField(blank=True, verbose_name="Descripción del Producto")
    icon_class = models.CharField(max_length=50, default="fas fa-cube", help_text="Icono FontAwesome para el panel")

    class Meta:
        verbose_name = "Producto SaaS"
        verbose_name_plural = "Productos SaaS"

    def __str__(self):
        return self.name

class ProductPlan(BaseModel):
    """
    DEFINICIÓN DE PLANES:
    Cada producto puede tener múltiples planes (Gratis, Pro, etc.)
    """
    product = models.ForeignKey(SaaSProduct, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=50, verbose_name="Nombre del Plan")
    description = models.TextField(blank=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    duration_days = models.IntegerField(default=30, help_text="Duración en días. 0 para ilimitado/lifetime.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Plan de Producto"
        verbose_name_plural = "Planes de Productos"

    def __str__(self):
        return f"{self.product.name} - {self.name} (${self.price_usd})"

class ProductLicense(BaseModel):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="product_licenses",
        verbose_name="Organización"
    )
    product = models.ForeignKey(
        SaaSProduct, 
        on_delete=models.CASCADE, 
        related_name="active_licenses",
        verbose_name="Producto Contratado"
    )
    plan = models.ForeignKey(
        ProductPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="licenses",
        verbose_name="Plan Actual"
    )
    
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    
    # Mantenemos plan_type como fallback o legacy
    plan_type = models.CharField(max_length=20, default='free', blank=True)

    class Meta:
        unique_together = ('organization', 'product')
        verbose_name = "Licencia de Producto"
        verbose_name_plural = "Licencias de Productos"

    def __str__(self):
        return f"{self.organization.name} -> {self.product.name} ({self.plan.name if self.plan else self.plan_type})"

class Payment(BaseModel):
    """
    REGISTRO MAESTRO DE INGRESOS:
    Soporta pagos manuales del admin y automáticos de apps externas.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="payments")
    license = models.ForeignKey(ProductLicense, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    plan = models.ForeignKey(ProductPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments_applied")
    
    # Montos y Monedas
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto en USD")
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Tasa de Cambio (BCV)")
    amount_ves = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto en Bolívares")
    
    # Detalles de la Transacción
    PAYMENT_METHODS = (
        ('pago_movil', 'Pago Móvil'),
        ('zelle', 'Zelle'),
        ('binance', 'Binance Pay'),
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='pago_movil')
    reference = models.CharField(max_length=100, help_text="ID de transacción / Referencia")
    
    # Estado y Auditoría
    status = models.CharField(max_length=20, default='completed', choices=(
        ('pending', 'Verificación Pendiente'),
        ('completed', 'Cargado con Éxito'),
        ('failed', 'Rechazado'),
        ('voided', 'Anulado')
    ))
    # Saber qué App Orquestada envió el cobro (si fue automático)
    source_product = models.ForeignKey(SaaSProduct, on_delete=models.SET_NULL, null=True, blank=True)
    
    notes = models.TextField(blank=True, verbose_name="Notas de Auditoría")

    class Meta:
        verbose_name = "Cobro / Pago"
        verbose_name_plural = "Cobros / Pagos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name} - ${self.amount_usd} ({self.get_status_display()})"
