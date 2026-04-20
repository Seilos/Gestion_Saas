import os
from dotenv import load_dotenv
import requests

load_dotenv()

CLARAPOS_FUNCTIONS_URL = os.environ.get('VITE_SUPABASE_URL', '').rstrip('/') + "/functions/v1"

def clarapos_api_headers():
    # Nota: la edge function register-owner no requiere authorization de un service_role,
    # pero para buenas practicas se envia el ANON_KEY que se consigue en public
    anon_key = os.environ.get('VITE_SUPABASE_ANON_KEY', '')
    return {
        "Authorization": f"Bearer {anon_key}",
        "Content-Type": "application/json"
    }

def crear_tenant_clarapos(nombre, email, password, nombre_empresa):
    """
    Llama a la edge function de ClaraPOS 'register-owner'.
    Crea el tenant, la primera empresa, asigna roles y establece el usuario default.
    Retorna un diccionario con tenantId, empresaId, y userId o raise ValueError
    """
    url = f"{CLARAPOS_FUNCTIONS_URL}/register-owner"
    payload = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "nombre_empresa": nombre_empresa
    }

    try:
        response = requests.post(url, json=payload, headers=clarapos_api_headers(), timeout=15)
        
        datos = response.json()
        if response.status_code == 200 and datos.get("success"):
            return {
                "tenantId": datos.get("tenantId"),
                "empresaId": datos.get("empresaId"),
                "userId": datos.get("userId")
            }
        else:
            error_msg = datos.get("error", "Error desconocido al registrar en ClaraPOS")
            raise ValueError(f"Fallo registro en ClaraPOS ({response.status_code}): {error_msg}")
    except requests.RequestException as e:
        raise ValueError(f"No se pudo conectar a la API de ClaraPOS: {e}")
