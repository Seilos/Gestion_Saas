import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

BCV_URL = "https://www.bcv.org.ve/"

def parse_bcv_rate():
    try:
        # Custom headers to act as a normal browser to prevent blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        
        # Desactivando warnings de certificado por seguridad en sitios gubernamentales a veces
        requests.packages.urllib3.disable_warnings() 
        response = requests.get(BCV_URL, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # The BCV website typically holds the USD rate inside an element with ID 'dolar'
        # Inside that, there's usually a strong tag containing the rate in format "##,####"
        dolar_div = soup.find(id='dolar')
        
        if not dolar_div:
            raise ValueError("No se encontró el contenedor del ID 'dolar' en la web del BCV")
            
        rate_text = dolar_div.find('strong').text.strip()
        
        # Parsing format "36,2514" to Decimal("36.2514")
        cleaned_rate = rate_text.replace(',', '.')
        rate_value = Decimal(cleaned_rate)
        
        # Also let's try to find the date of the value
        # Usually it's in a span or div with class 'date-display-single'
        date_element = soup.find('span', class_='date-display-single')
        date_text = date_element.text.strip() if date_element else None
        
        return {
            "source": "BCV",
            "value": rate_value,
            "date_text": date_text, # Ej: '19 de Abril de 2026'
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error scraping BCV: {e}")
        return {
            "source": "BCV",
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test script locally
    print("Fetching BCV Rate...")
    print(parse_bcv_rate())
