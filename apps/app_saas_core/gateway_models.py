"""
Modelo para las claves API de los servicios satélite del ecosistema Nexo21.
Cada clave está vinculada a un SaaSProduct específico y permite al
License Gateway saber qué producto está consultando.
"""
import uuid
import secrets
from django.db import models
from django.conf import settings
from .models import SaaSProduct


def generate_service_key():
    """Genera una clave API segura con prefijo identificable (nxk_...)."""
    return f"nxk_{secrets.token_urlsafe(32)}"


class ServiceAPIKey(models.Model):
    """
    Clave API segura por servicio satélite.

    Ejemplo de uso en Clara Library:
        headers = {"X-Service-Key": "nxk_abc123..."}
        requests.get("http://nexo21.app/api/gateway/license/check/?org=mi-empresa", headers=headers)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        SaaSProduct,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="Producto Satélite"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Alias de la clave",
        help_text="Ej: 'Producción Railway', 'Dev Local'"
    )
    key = models.CharField(
        max_length=128,
        unique=True,
        default=generate_service_key,
        editable=False,
        verbose_name="Clave API"
    )
    is_active = models.BooleanField(default=True, verbose_name="¿Activa?")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    last_used_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Último uso",
        help_text="Actualizamos esto con cada llamada exitosa al Gateway."
    )
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de revocación")

    class Meta:
        verbose_name = "API Key de Servicio"
        verbose_name_plural = "API Keys de Servicios"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.product.name}] {self.name} — {'✅ Activa' if self.is_active else '🚫 Revocada'}"

    def revoke(self, by_user=None):
        """Revoca la clave de forma segura."""
        from django.utils import timezone
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save()
