from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app_saas_auth.models import Organization
from .models import SaaSProduct
from .forms import SaaSProductForm, OrganizationWithProductsForm

class GlobalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = "core/organization_list.html"
    context_object_name = "organizations"

    def get_queryset(self):
        # Usamos prefetch_related para evitar el problema de N+1 consultas al listar licencias
        return Organization.objects.all().prefetch_related('product_licenses__product').order_by('-created_at')

class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationWithProductsForm
    template_name = "core/partials/organization_form.html"
    success_url = reverse_lazy('org_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('org_create')
        context['submit_text'] = 'Crear Organización'
        context['success_message'] = 'La organización y sus licencias iniciales han sido creadas.'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Guardar licencias después de crear la organización
        form.save_licenses(self.object, self.request.user)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {'message': self.get_context_data()['success_message']})
        return response

class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organization
    form_class = OrganizationWithProductsForm
    template_name = "core/partials/organization_form.html"
    success_url = reverse_lazy('org_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('org_update', kwargs={'pk': self.object.pk})
        context['submit_text'] = 'Actualizar Organización'
        context['success_message'] = 'Información del cliente y licencias actualizada.'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Sincronizar licencias
        form.save_licenses(self.object, self.request.user)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {'message': self.get_context_data()['success_message']})
        return response

def toggle_organization_status(request, pk):
    # Protegido manualmente para funciones sencillas
    if not request.user.is_authenticated:
        return redirect('login')
        
    org = get_object_or_404(Organization, pk=pk)
    org.is_active = not org.is_active
    org.save()
    if request.htmx:
        return redirect('org_list')
    return redirect('org_list')

# --- VISTAS DE PRODUCTOS ---

class ProductListView(LoginRequiredMixin, ListView):
    model = SaaSProduct
    template_name = "core/product_list.html"
    context_object_name = "products"
    
    def get_queryset(self):
        # Ocultamos los que están borrados lógicamente (deleted_at)
        return SaaSProduct.objects.filter(deleted_at__isnull=True).order_by('-created_at')

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = SaaSProduct
    form_class = SaaSProductForm
    template_name = "core/partials/product_form.html"
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('product_create')
        context['submit_text'] = 'Crear Producto'
        context['success_message'] = 'El producto ha sido registrado en el ecosistema.'
        return context

    def form_valid(self, form):
        # Auditoría: asignar quién crea
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {
                'message': self.get_context_data()['success_message']
            })
        return response

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = SaaSProduct
    form_class = SaaSProductForm
    template_name = "core/partials/product_form.html"
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('product_update', kwargs={'pk': self.object.pk})
        context['submit_text'] = 'Actualizar Producto'
        context['success_message'] = 'Información del producto actualizada.'
        return context

    def form_valid(self, form):
        # Auditoría: asignar quién actualiza
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {
                'message': self.get_context_data()['success_message']
            })
        return response

def toggle_product_status(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
        
    product = get_object_or_404(SaaSProduct, pk=pk)
    product.is_active = not product.is_active
    if not product.is_active:
        from django.utils import timezone
        product.deactivated_at = timezone.now()
        product.deactivated_by = request.user
    product.save()
    return redirect('product_list')
