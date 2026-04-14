from django import forms
from django.utils import timezone
from app_saas_auth.models import Organization
from .models import SaaSProduct, ProductLicense

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
    products = forms.ModelMultipleChoiceField(
        queryset=SaaSProduct.objects.filter(is_active=True, deleted_at__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Apps Satélites Activas"
    )

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
        if self.instance.pk:
            # Marcamos los productos que ya tienen licencia activa
            self.fields['products'].initial = self.instance.product_licenses.filter(
                deleted_at__isnull=True
            ).values_list('product', flat=True)

    def save_licenses(self, organization, user):
        """Sincroniza las licencias según la selección del formulario."""
        selected_products = self.cleaned_data.get('products', [])
        
        # 1. Soft Delete de licencias desmarcadas
        organization.product_licenses.filter(deleted_at__isnull=True).exclude(product__in=selected_products).update(
            deleted_at=timezone.now(),
            deleted_by=user,
            is_active=False
        )

        # 2. Crear o reactivar licencias seleccionadas
        for product in selected_products:
            license, created = ProductLicense.objects.get_or_create(
                organization=organization,
                product=product,
                defaults={'created_by': user}
            )
            if not created and license.deleted_at:
                license.deleted_at = None
                license.deleted_by = None
                license.is_active = True
                license.save()
