from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from app_saas_auth.models import Organization
from .models import SaaSProduct, ProductLicense, Payment, ProductPlan
from .forms import SaaSProductForm, OrganizationWithProductsForm, PaymentForm, ProductPlanForm

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
        form.save_licenses(self.object, self.request.user, self.request.POST)
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
        form.save_licenses(self.object, self.request.user, self.request.POST)
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
        return ProductLicense.objects.filter(deleted_at__isnull=True).select_related('organization', 'product', 'plan').order_by('expires_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        now = timezone.now()
        next_week = now + timezone.timedelta(days=7)
        
        # Licencias que vencen en los próximos 7 días (y que no sean ilimitadas)
        context['expiring_7d_count'] = ProductLicense.objects.filter(
            deleted_at__isnull=True,
            is_active=True,
            expires_at__gt=now,
            expires_at__lte=next_week
        ).count()
        
        # Licencias activas totales
        context['active_count'] = ProductLicense.objects.filter(
            deleted_at__isnull=True,
            is_active=True
        ).count()
        
        return context

def renew_license(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    license = get_object_or_404(ProductLicense, pk=pk)
    if not license.plan or license.plan.duration_days == 0:
        # Si es ilimitado, no hace falta renovar, pero nos aseguramos que esté activo
        license.is_active = True
        license.expires_at = None
    else:
        # Sumar la duración del plan
        base_date = license.expires_at if license.expires_at and license.expires_at > timezone.now() else timezone.now()
        license.expires_at = base_date + timezone.timedelta(days=license.plan.duration_days)
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
        
        # --- LÓGICA DE RENOVACIÓN AUTOMÁTICA AL COBRAR ---
        if license.plan and license.plan.duration_days > 0:
            base_date = license.expires_at if license.expires_at and license.expires_at > timezone.now() else timezone.now()
            license.expires_at = base_date + timezone.timedelta(days=license.plan.duration_days)
            license.is_active = True
            license.save()
        elif license.plan and license.plan.duration_days == 0:
            license.expires_at = None
            license.is_active = True
            license.save()

        response = super().form_valid(form)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {
                'message': f"¡Cobro de ${form.instance.amount_usd} registrado con éxito!"
            })
        return response

# --- GESTIÓN DE PLANES ---

class ProductPlanListView(LoginRequiredMixin, ListView):
    model = ProductPlan
    template_name = "core/plan_list.html"
    context_object_name = "plans"

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductPlan.objects.filter(product_id=product_id, deleted_at__isnull=True).order_by('price_usd')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(SaaSProduct, pk=self.kwargs.get('product_id'))
        return context

class ProductPlanCreateView(LoginRequiredMixin, CreateView):
    model = ProductPlan
    form_class = ProductPlanForm
    template_name = "core/partials/plan_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        context['product'] = get_object_or_404(SaaSProduct, pk=product_id)
        context['form_action'] = reverse_lazy('plan_create', kwargs={'product_id': product_id})
        return context

    def form_valid(self, form):
        product_id = self.kwargs.get('product_id')
        form.instance.product = get_object_or_404(SaaSProduct, pk=product_id)
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        if self.request.htmx:
            return redirect('plan_list', product_id=product_id)
        return response

    def get_success_url(self):
        return reverse_lazy('plan_list', kwargs={'product_id': self.kwargs.get('product_id')})
