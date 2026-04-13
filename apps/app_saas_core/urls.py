from django.urls import path
from .views import GlobalDashboardView

urlpatterns = [
    path('', GlobalDashboardView.as_view(), name='global_dashboard'),
]
