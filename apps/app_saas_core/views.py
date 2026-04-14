from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from app_saas_auth.models import Organization
from .models import SaaSProduct, ProductLicense, Payment
from .forms import SaaSProductForm, OrganizationWithProductsForm, PaymentForm

# --- DASHBOARD ---
class GlobalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

# --- ORGANIZACIONES ---
class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = "core/organization_list.html"
    context_object_name = "organizations"

    def get_queryset(self):
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
        form.save_licenses(self.object, self.request.user)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {'message': self.get_context_data()['success_message']})
        return response

def toggle_organization_status(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    org = get_object_or_404(Organization, pk=pk)
    org.is_active = not org.is_active
    org.save()
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

# --- SUSCRIPCIONES Y LICENCIAS ---

class SubscriptionListView(LoginRequiredMixin, ListView):
    model = ProductLicense
    template_name = "core/subscription_list.html"
    context_object_name = "subscriptions"

    def get_queryset(self):
        return ProductLicense.objects.filter(deleted_at__isnull=True).select_related('organization', 'product').order_by('expires_at')

def renew_license(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    license = get_object_or_404(ProductLicense, pk=pk)
    # Extender 30 días desde hoy o desde el vencimiento si es futuro
    base_date = license.expires_at if license.expires_at and license.expires_at > timezone.now() else timezone.now()
    from datetime import timedelta
    license.expires_at = base_date + timedelta(days=30)
    license.is_active = True
    license.updated_by = request.user
    license.save()
    
    return redirect('subscription_list')

def toggle_license_status(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    license = get_object_or_404(ProductLicense, pk=pk)
    license.is_active = not license.is_active
    if not license.is_active:
        license.deactivated_at = timezone.now()
        license.deactivated_by = request.user
    else:
        license.deactivated_at = None
        license.deactivated_by = None
    license.save()
    
    return redirect('subscription_list')

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "core/partials/payment_form.html"
    success_url = reverse_lazy('subscription_list')

    def get_initial(self):
        initial = super().get_initial()
        license_id = self.kwargs.get('license_id')
        if license_id:
            license = get_object_or_404(ProductLicense, pk=license_id)
            initial['license'] = license
            initial['organization'] = license.organization
            initial['exchange_rate'] = 36.50
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        license_id = self.kwargs.get('license_id')
        context['license'] = get_object_or_404(ProductLicense, pk=license_id)
        context['form_action'] = reverse_lazy('payment_create', kwargs={'license_id': license_id})
        return context

    def form_valid(self, form):
        license_id = self.kwargs.get('license_id')
        license = get_object_or_404(ProductLicense, pk=license_id)
        form.instance.organization = license.organization
        form.instance.license = license
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {
                'message': f"¡Cobro de ${form.instance.amount_usd} registrado con éxito!"
            })
        return response
