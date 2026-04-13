from django.urls import path
from .views import GlobalDashboardView, OrganizationListView, OrganizationCreateView, OrganizationUpdateView, toggle_organization_status

urlpatterns = [
    path('', GlobalDashboardView.as_view(), name='global_dashboard'),
    path('organizaciones/', OrganizationListView.as_view(), name='org_list'),
    path('organizaciones/crear/', OrganizationCreateView.as_view(), name='org_create'),
    path('organizaciones/editar/<uuid:pk>/', OrganizationUpdateView.as_view(), name='org_update'),
    path('organizaciones/toggle/<uuid:pk>/', toggle_organization_status, name='org_toggle'),
]
