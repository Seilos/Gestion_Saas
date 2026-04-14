import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("--- ESTRUCTURA DE TABLAS ACTUALES ---")
for table in tables:
    table_name = table[0]
    # Filter to show only relevant apps tables (to avoid cluttering with django internals)
    if 'app_saas' in table_name:
        print(f"\nTABLA: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"{'ID':<4} | {'Nombre':<20} | {'Tipo':<15} | {'NotNull':<8} | {'PK':<3}")
        print("-" * 60)
        for col in columns:
            id_col, name, d_type, notnull, dflt, pk = col
            print(f"{id_col:<4} | {name:<20} | {d_type:<15} | {notnull:<8} | {pk:<3}")

conn.close()
