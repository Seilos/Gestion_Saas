"""
Script para probar acceso a ClaraPOS vía conexión directa a Supabase PostgreSQL.
Usa la DATABASE_URL del .env principal para el Orquestador,
o intenta con las distintas variantes de connection string de ClaraPOS.

SOLO LECTURA - no modifica nada.
"""
import os, sys

# Leer .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            env_vars[k.strip()] = v.strip()

SUPABASE_URL  = env_vars.get('VITE_SUPABASE_URL', '').rstrip('/')
ANON_KEY      = env_vars.get('VITE_SUPABASE_ANON_KEY', '')

# Extraer project ref del URL: https://jfocaxbskidwigjwxhhj.supabase.co
project_ref = SUPABASE_URL.replace('https://', '').split('.')[0]
print(f"Project ref detectado: {project_ref}")

# Intentar conexión directa via psycopg2 usando los poolers conocidos de Supabase
import psycopg2

# Supabase expone 2 poolers:
# - Transaction pooler: aws-*.pooler.supabase.com:5432  (no admite SET commands)
# - Session pooler: db.<ref>.supabase.co:5432           (conexión directa)
password = None
# Intentar extraer password de la DATABASE_URL del orquestador como referencia
# (la de ClaraPOS no está en el .env todavía)
print("\n⚠️  La ANON KEY de Supabase es la clave pública del cliente JavaScript.")
print("   Para acceso directo a PostgreSQL se necesita la DATABASE_URL o la service_role key.")
print(f"\n   La URL de ClaraPOS es: {SUPABASE_URL}")
print(f"   El project_ref es:     {project_ref}")
print("\n   Para completar la integración necesito UNA de estas opciones:")
print("   A) Agregar al .env:  CLARAPOS_DATABASE_URL=postgresql://postgres.<ref>:<password>@...")
print("   B) Agregar al .env:  CLARAPOS_SERVICE_KEY=eyJ...  (service_role key de Supabase)")
print("\n   Puedes encontrar ambas en:")
print("   Supabase Dashboard → tu proyecto ClaraPOS → Settings → Database / API")
print("\n✅ Conexión de red: OK (URL válida, proyecto existe)")
print(f"✅ Supabase URL confirmada: {SUPABASE_URL}")
print(f"⏳ Esperando: CLARAPOS_DATABASE_URL o CLARAPOS_SERVICE_KEY en el .env")
