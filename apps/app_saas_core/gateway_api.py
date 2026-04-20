"""
🔐 NEXO21 LICENSE GATEWAY API
=================================
REST API que los servicios satélite (Clara Library, Clara POS, etc.)
consultan para verificar si una organización tiene una licencia activa.

Autenticación: Header  X-Service-Key: <clave_del_producto>
Endpoint:      GET /api/gateway/license/check/

Diseñado para ser agnóstico: cualquier SaaS puede integrarse sin
conocer la estructura interna del Orquestador.
"""
from ninja import NinjaAPI, Schema
from ninja.security import APIKeyHeader
from typing import Optional
from django.utils import timezone
from .models import ProductLicense, SaaSProduct
from .gateway_models import ServiceAPIKey


class ServiceKeyAuth(APIKeyHeader):
    param_name = "X-Service-Key"

    def authenticate(self, request, key):
        try:
            service_key = ServiceAPIKey.objects.select_related('product').get(
                key=key,
                is_active=True
            )
            # Adjuntar el producto asociado al request para usarlo en los endpoints
            request.authorized_product = service_key.product
            return service_key
        except ServiceAPIKey.DoesNotExist:
            return None


gateway_api = NinjaAPI(
    title="Nexo21 License Gateway",
    description="API de autorización de licencias para el ecosistema Nexo21.",
    version="1.0.0",
    urls_namespace="gateway"
)


class LicenseCheckResponse(Schema):
    authorized: bool
    organization_slug: str
    product_slug: str
    plan_name: Optional[str] = None
    expires_at: Optional[str] = None
    message: str


@gateway_api.get(
    "/license/check/",
    auth=ServiceKeyAuth(),
    response=LicenseCheckResponse,
    summary="Verificar licencia de una organización",
    description=(
        "El SaaS satélite envía su X-Service-Key y el slug de la organización. "
        "El orquestador responde si la licencia está activa, suspendida o inexistente."
    )
)
def check_license(request, org: str):
    """
    Parámetro: ?org=slug-de-la-organizacion

    Responde si la organización tiene una licencia activa para el producto
    asociado a la API Key que realizó la llamada.
    """
    product = request.authorized_product

    try:
        license = ProductLicense.objects.select_related('plan', 'organization').get(
            product=product,
            organization__slug=org,
            deleted_at__isnull=True
        )
    except ProductLicense.DoesNotExist:
        return {
            "authorized": False,
            "organization_slug": org,
            "product_slug": product.slug,
            "message": "Licencia no encontrada para esta organización."
        }

    # Verificar que esté activa y no vencida
    if not license.is_active:
        return {
            "authorized": False,
            "organization_slug": org,
            "product_slug": product.slug,
            "plan_name": license.plan.name if license.plan else None,
            "message": "Licencia suspendida. Contacte al administrador."
        }

    if license.expires_at and license.expires_at < timezone.now():
        return {
            "authorized": False,
            "organization_slug": org,
            "product_slug": product.slug,
            "plan_name": license.plan.name if license.plan else None,
            "expires_at": license.expires_at.isoformat(),
            "message": f"Licencia vencida el {license.expires_at.strftime('%d/%m/%Y')}."
        }

    return {
        "authorized": True,
        "organization_slug": org,
        "product_slug": product.slug,
        "plan_name": license.plan.name if license.plan else "Sin plan",
        "expires_at": license.expires_at.isoformat() if license.expires_at else None,
        "message": "Acceso autorizado."
    }
