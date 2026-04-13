from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')

@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'organization', 'role', 'is_premium', 'is_staff')
    list_filter = ('role', 'is_premium', 'organization')
    fieldsets = UserAdmin.fieldsets + (
        ('Información SaaS', {'fields': ('organization', 'role', 'is_premium', 'avatar_url')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información SaaS', {'fields': ('organization', 'role', 'is_premium', 'avatar_url')}),
    )
