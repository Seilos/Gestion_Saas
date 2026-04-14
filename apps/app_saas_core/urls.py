from django.urls import path
from .views import (
    GlobalDashboardView, OrganizationListView, OrganizationCreateView, 
    OrganizationUpdateView, toggle_organization_status,
    ProductListView, ProductCreateView, ProductUpdateView, toggle_product_status,
    SubscriptionListView, renew_license, toggle_license_status, PaymentCreateView
)

urlpatterns = [
    path('', GlobalDashboardView.as_view(), name='global_dashboard'),
    
    # Organizaciones
    path('organizaciones/', OrganizationListView.as_view(), name='org_list'),
    path('organizaciones/crear/', OrganizationCreateView.as_view(), name='org_create'),
    path('organizaciones/editar/<uuid:pk>/', OrganizationUpdateView.as_view(), name='org_update'),
    path('organizaciones/toggle/<uuid:pk>/', toggle_organization_status, name='org_toggle'),
    
    # Productos
    path('productos/', ProductListView.as_view(), name='product_list'),
    path('productos/crear/', ProductCreateView.as_view(), name='product_create'),
    path('productos/editar/<uuid:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('productos/toggle/<uuid:pk>/', toggle_product_status, name='product_toggle'),

    # Suscripciones
    path('suscripciones/', SubscriptionListView.as_view(), name='subscription_list'),
    path('suscripciones/renovar/<uuid:pk>/', renew_license, name='license_renew'),
    path('suscripciones/toggle/<uuid:pk>/', toggle_license_status, name='license_toggle'),
    path('suscripciones/cobrar/<uuid:license_id>/', PaymentCreateView.as_view(), name='payment_create'),
]
