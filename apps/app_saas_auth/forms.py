from django import forms
from .models import Organization

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Servicios Médicos C.A.'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ej-servicios-medicos'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
