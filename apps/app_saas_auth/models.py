import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class Organization(models.Model):
    """
    Representa a un Tenant (Empresa/Organización) en el ecosistema Nexo21.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Nombre de la Organización")
    slug = models.SlugField(unique=True, help_text="Identificador único para la URL o subdominios")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Modelo de usuario personalizado para Nexo21 Orchestrator.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="members",
        help_text="La organización a la que pertenece este usuario."
    )
    
    # Roles Globales (Nivel Orquestador)
    ROLE_CHOICES = (
        ('super_admin', 'Súper Administrador Nexo21'),
        ('tenant_admin', 'Administrador de Inquilino'),
        ('tenant_staff', 'Personal de Inquilino'),
        ('freelancer', 'Usuario Independiente'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='freelancer')
    
    is_premium = models.BooleanField(default=False)
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
