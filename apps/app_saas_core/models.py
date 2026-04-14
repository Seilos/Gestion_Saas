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

class ProductLicense(BaseModel):
    """
    CONTROL DE ACCESO (Licencias):
    Relaciona a tus Organizaciones (Clientes) con tus Productos.
    """
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="product_licenses",
        verbose_name="Cliente/Organización"
    )
    product = models.ForeignKey(
        SaaSProduct, 
        on_delete=models.CASCADE, 
        related_name="active_licenses",
        verbose_name="Producto Contratado"
    )
    
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    
    PLAN_LEVELS = (
        ('free', 'Gratuito'),
        ('pro', 'Profesional'),
        ('enterprise', 'Enterprise'),
    )
    plan_type = models.CharField(max_length=20, choices=PLAN_LEVELS, default='free')

    class Meta:
        unique_together = ('organization', 'product')
        verbose_name = "Licencia de Producto"
        verbose_name_plural = "Licencias de Productos"

    def __str__(self):
        return f"{self.organization.name} -> {self.product.name} ({self.plan_type})"
