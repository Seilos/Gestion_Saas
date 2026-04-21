import sys
import os
from django.apps import AppConfig

class BcvServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bcv_service'

    def ready(self):
        # Evitar arrancar el scheduler si estamos corriendo migraciones o comandos de admin
        if os.environ.get('RUN_MAIN', None) != 'true' and 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
             return
             
        # Importamos aquí para evitar problemas circulares
        from bcv_service import scheduler
        scheduler.start_scheduler()
