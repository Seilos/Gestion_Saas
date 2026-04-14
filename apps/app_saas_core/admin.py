from django.contrib import admin
from .models import SaaSProduct, ProductLicense

class BaseSaaSAdmin(admin.ModelAdmin):
    """Clase base para administrar los campos de auditoría de forma limpia."""
    readonly_fields = (
        'id', 'created_at', 'created_by', 
        'updated_at', 'updated_by', 
        'deleted_at', 'deleted_by', 
        'deactivated_at', 'deactivated_by'
    )
    
    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario que crea o edita."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SaaSProduct)
class SaaSProductAdmin(BaseSaaSAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)} # Autocompleta el slug al escribir el nombre
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'name', 'slug', 'description', 'icon_class', 'is_active')
        }),
        ('Auditoría y Estado', {
            'classes': ('collapse',), # Oculto por defecto para limpiar la vista
            'fields': (
                'created_at', 'created_by', 
                'updated_at', 'updated_by', 
                'deactivated_at', 'deactivated_by',
                'deleted_at', 'deleted_by'
            )
        }),
    )

@admin.register(ProductLicense)
class ProductLicenseAdmin(BaseSaaSAdmin):
    list_display = ('organization', 'product', 'plan_type', 'is_active', 'expires_at')
    list_filter = ('plan_type', 'is_active', 'product', 'organization')
    search_fields = ('organization__name', 'product__name')
    
    fieldsets = (
        ('Configuración de Licencia', {
            'fields': ('organization', 'product', 'plan_type', 'expires_at', 'is_active')
        }),
        ('Registro de Auditoría', {
            'classes': ('collapse',),
            'fields': (
                'created_at', 'created_by', 
                'updated_at', 'updated_by',
                'deactivated_at', 'deactivated_by'
            )
        }),
    )
