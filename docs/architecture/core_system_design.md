# 🏛️ Diseño de Arquitectura: Ecosistema Nexo21
## Sistema Orquestador Multi-Tenant & Multi-App (Local-First Pro)

> **Versión:** 1.1  
> **Estado:** Documentación Consolidada  
> **Autores:** Consejo de 16 IA Experts - Nexo21

---

## 1. Visión General
Nexo21 es un entorno orquestador diseñado para albergar, cobrar y distribuir aplicaciones SaaS con una estética premium y resiliencia offline.

## 2. Pilares Estratégicos

### A. Multitenancy & Aislamiento
- **Aislamiento Lógico**: Uso de `tenant_id` en todas las tablas con políticas de **Supabase RLS**.
- **RBAC (Access Control)**: Sistema jerárquico de roles (Súper Admin, Admin Inquilino, Operador, Auditor).

### B. Local-First (PowerSync)
- **Sincronización Bidireccional**: Los clientes operan sobre SQLite local.
- **Reactividad Real-Time**: La UI se actualiza automáticamente ante cambios en la DB local (vía PowerSync streams) sin recargar la página.

### C. API-First con Django Ninja
- **Backend Moderno**: Uso de Django Ninja para una comunicación rápida, tipada (Pydantic) y documentada (Swagger).
- **Mutaciones**: Todas las operaciones de escritura pasan por una capa de validación en Django antes de llegar a la DB principal.

## 3. Características Avanzadas (Enterprise Ready)

1.  **Motor Bi-Monetario (USD/VED)**:
    - Registro integral de transacciones en ambas monedas.
    - Integración automática con tazas oficiales (BCV) para conversión en tiempo real.
2.  **Sistema de Feature Flags**: Activa/Desactiva módulos (POS, Library, Nomina) dinámicamente según el plan del Tenant.
3.  **Audit Trail & Observabilidad**:
    - Registro histórico de cada acción por usuario/tenant.
    - Implementación de **Correlation IDs** para trazabilidad de errores entre apps.
4.  **UX Reactiva (HTMX)**: Interacciones de servidor sin recarga de página parcial.

## 4. Estructura de Aplicaciones

```text
/apps/
├── core/                # Gestión de Tenants y Configuración Global
├── billing/             # Planes, Suscripciones, Pagos (Binance/Pago Móvil)
├── identity/            # Auth, Roles y Perfiles
├── common/             # Utilidades, Tasa BCV, Componentes UI Atómicos
└── saas_satellites/     # Apps instalables (Library, POS, etc.)
```

## 5. Stock Tecnológico Consolidado
- **Lenguaje**: Python 3.x
- **Framework**: Django 5.x + Django Ninja
- **Frontend**: Bootstrap 5 (Custom Premium) + HTMX + Service Workers (PWA)
- **DB (Source of Truth)**: Supabase / PostgreSQL
- **DB (Local Client)**: SQLite (vía PowerSync Web SDK)
- **Asincronía**: Celery / Taskiq (para conciliación de pagos)

---
"Un ecosistema, infinitas posibilidades. Nexo21 Core."
