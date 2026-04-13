from django.contrib.auth.mixins import LoginRequiredMixin
from app_saas_auth.models import Organization
from app_saas_auth.forms import OrganizationForm

class GlobalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = "core/organization_list.html"
    context_object_name = "organizations"

class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "core/partials/organization_form.html"
    success_url = reverse_lazy('org_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('org_create')
        context['submit_text'] = 'Crear Organización'
        context['success_message'] = 'La organización ha sido creada correctamente.'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {'message': self.get_context_data()['success_message']})
        return response

class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "core/partials/organization_form.html"
    success_url = reverse_lazy('org_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action'] = reverse_lazy('org_update', kwargs={'pk': self.object.pk})
        context['submit_text'] = 'Actualizar Organización'
        context['success_message'] = 'La organización ha sido actualizada correctamente.'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            return render(self.request, "core/partials/organization_success.html", {'message': self.get_context_data()['success_message']})
        return response

def toggle_organization_status(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    org.is_active = not org.is_active
    org.save()
    if request.htmx:
        # Si es HTMX, simplemente devolvemos la misma página para que la tabla se refresque
        # o podríamos devolver solo el fragmento de la fila (más avanzado)
        return redirect('org_list')
    return redirect('org_list')
