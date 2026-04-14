from django import forms
from django.utils import timezone
from app_saas_auth.models import Organization
from .models import SaaSProduct, ProductLicense, Payment, ProductPlan

class SaaSProductForm(forms.ModelForm):
    class Meta:
        model = SaaSProduct
        fields = ['name', 'slug', 'description', 'icon_class', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'Ej: Nexo ERP'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'ej-nexo-erp'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-3 px-4', 'rows': 3, 'placeholder': 'Breve descripción del producto...'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'fas fa-cube'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OrganizationWithProductsForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'Nombre de la empresa...'}),
            'slug': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'slug-unico'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtenemos todos los productos y planes para pasarlos al template
        self.available_products = SaaSProduct.objects.filter(is_active=True, deleted_at__isnull=True).prefetch_related('plans')
        
        # Diccionario de licencias actuales para pre-cargar el select en edición
        self.current_licenses = {}
        if self.instance.pk:
            self.current_licenses = {
                str(lic.product_id): str(lic.plan_id) if lic.plan_id else "none"
                for lic in self.instance.product_licenses.filter(deleted_at__isnull=True)
            }

    def save_licenses(self, organization, user, post_data):
        """
        Sincroniza licencias leyendo los campos dinámicos 'product_{uuid}_plan' del POST.
        """
        active_product_ids = []
        
        for product in self.available_products:
            plan_id = post_data.get(f'product_{product.id}_plan')
            
            if plan_id and plan_id != "none":
                active_product_ids.append(product.id)
                plan = ProductPlan.objects.get(pk=plan_id)
                
                license, created = ProductLicense.objects.get_or_create(
                    organization=organization,
                    product=product,
                    defaults={'created_by': user, 'plan': plan}
                )
                
                # Si ya existía, actualizamos el plan y reactivamos si estaba borrado
                license.plan = plan
                license.is_active = True
                license.deleted_at = None
                
                # Lógica de vencimiento: 
                # Si no tiene fecha y el plan tiene duración, la calculamos desde hoy.
                # Si el plan es ilimitado (0), nos aseguramos de que sea None.
                if plan.duration_days > 0:
                    if not license.expires_at:
                        license.expires_at = timezone.now() + timezone.timedelta(days=plan.duration_days)
                else:
                    license.expires_at = None
                
                license.save()

        # Desactivar/Soft-delete de productos que ya no están seleccionados
        organization.product_licenses.filter(deleted_at__isnull=True).exclude(product_id__in=active_product_ids).update(
            deleted_at=timezone.now(),
            deleted_by=user,
            is_active=False
        )

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_usd', 'exchange_rate', 'amount_ves', 'method', 'reference', 'notes']
        widgets = {
            'amount_usd': forms.NumberInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': '0.00', 'step': '0.01'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'Tasa BCV', 'step': '0.01'}),
            'amount_ves': forms.NumberInput(attrs={'class': 'form-control rounded-pill px-4 bg-light', 'placeholder': 'Monto en Bs.', 'readonly': 'readonly'}),
            'method': forms.Select(attrs={'class': 'form-select rounded-pill px-4'}),
            'reference': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'Ref / Confirmación'}),
            'notes': forms.Textarea(attrs={'class': 'form-control rounded-3 px-4', 'rows': 2, 'placeholder': 'Observaciones adicionales...'}),
        }

class ProductPlanForm(forms.ModelForm):
    class Meta:
        model = ProductPlan
        fields = ['name', 'price_usd', 'duration_days', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'Ej: Plan Mensual Profesional'}),
            'price_usd': forms.NumberInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': '0.00', 'step': '0.01'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control rounded-pill px-4', 'placeholder': 'Días (ej: 30)'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-3 px-4', 'rows': 2, 'placeholder': '¿Qué incluye este plan?'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
