from django.shortcuts import render
from django.views.generic import TemplateView

class GlobalDashboardView(TemplateView):
    template_name = "core/dashboard.html"
