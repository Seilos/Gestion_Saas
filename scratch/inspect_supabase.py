import os
import sys
import django

# Asegurar que el directorio raíz está en el path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_nexo21.settings')
django.setup()

from django.db import connection

def list_tables_django():
    with connection.cursor() as cursor:
        # PostgreSQL syntax for listing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("--- TABLAS EN BASE DE DATOS ACTIVA (SUPABASE) ---")
        for table in tables:
            t_name = table[0]
            if 'app_saas' in t_name:
                print(f"\nTABLA: {t_name}")
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{t_name}'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"{'Columna':<25} | {'Tipo':<20} | {'Nullable':<8}")
                print("-" * 60)
                for col in columns:
                    name, dtype, nullable = col
                    print(f"{name:<25} | {dtype:<20} | {nullable:<8}")

if __name__ == "__main__":
    list_tables_django()
