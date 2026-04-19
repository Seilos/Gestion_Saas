# 📑 Log de Sesión: 19 de Abril, 2026 (Transición a Monorepo y API BCV)
## Proyecto: Ecosistema Nexo21 — Orquestador SaaS + DaaS

### 📝 Resumen Ejecutivo
En esta sesión, la arquitectura del proyecto evolucionó de un sistema monolítico a una infraestructura orientada a servicios (SOA / Monorepo). Se detectó la necesidad de utilizar la tasa del BCV no solo para el panel administrativo, sino también para futuras herramientas independientes (ERP, sitios como DolarVzla, etc.). Por tanto, se desarrolló un microservicio dedicado e independiente llamado **API BCV**, que cuenta con su propia configuración de base de datos aislada para garantizar seguridad y escalabilidad masiva.

---

### ✅ Hitos de la Sesión
1.  **Refactorización de Lanzadores**: Se optimizó agresivamente el archivo `run_nexo21.bat`, implementando vigilancia de puertos asíncrona, cierre preventivo de procesos conflictivos en el puerto `8080` y garantizando que la consola de desarrollo jamás se cierre de forma inesperada (uso de `cmd /k`).
2.  **Arquitectura Monorepo**: Creación de la carpeta `services/` para alojar aplicaciones/APIs secundarias que comparten el entorno de desarrollo local pero poseen repositorios de datos independientes.
3.  **Desarrollo del Scraper (Web Scraping)**: Implementación de la capa de extracción de datos usando `BeautifulSoup4`. El script simula un navegador legítimo y es capaz de parsear el DOM del portal oficial del Banco Central de Venezuela.
4.  **Despliegue del Microservicio de Datos (DaaS)**:
    *   Nuevo proyecto Django Ninja alojado en `services/api_bcv`.
    *   Archivo `.env` autónomo preparado para conectar con una instancia secundaria de Supabase (Cuenta B).
    *   Endpoint `GET /api/rates/bcv/latest` funcional.
5.  **Ejecución Dual (Concurrencia)**: Integración con éxito de los comandos de inicio rápido. El Panel Orquestador opera en `http://127.0.0.1:8080` y la API BCV en `http://127.0.0.1:8081` de manera simultánea.

---

### 📂 Archivos Modificados/Creados
| Archivo | Función |
|---|---|
| `run_nexo21.bat` | Script de inicialización robusto y persistente para el panel. |
| `services/api_bcv/run_api.bat` | Script de inicialización del microservicio BCV. |
| `services/api_bcv/bcv_service/scraper.py` | Motor de scraping y parseo de string a Decimal. |
| `services/api_bcv/bcv_service/api.py` | Definición de endpoints REST usando Django Ninja. |
| `services/api_bcv/bcv_service/models.py` | Tabla para caché histórico de tasas monetarias. |
| `.ai_experts/00_project_roadmap.md` | Actualizado esquema de directorios con el nuevo modelo SOA. |

---

### ⚠️ Pendientes Críticos
- [ ] **Integración Panel <-> API**: Conectar el formulario de pagos (`Payment`) del Orquestador para que llame a la nueva API BCV (`:8081/api/...`) al registrar un cobro, rellenando automáticamente el campo `exchange_rate`.
- [ ] **Métricas Financieras (MRR)**: Generar un reporte de Ingresos Recurrentes Mensuales en el Dashboard principal.
- [ ] **Gestión de Caché BCV**: Evitar el scraping excesivo si la tasa ya fue guardada el mismo día en la Base de Datos del servicio BCV.
- [ ] **Conexión a Supabase (Cuenta B)**: Rellenar el `.env` de la API con los datos reales del nuevo backend como servicio para independizarla de SQLite de forma final.

---

### 📊 Estado de Salud
**Indicador:** 🌐 **Ecosistema Expandiéndose**  
*El panel ya no está solo. Ha nacido el primer microservicio hermano preparado para el ecosistema público.*

---
*Documentado por Antigravity (IA) — 19 de Abril, 2026*
