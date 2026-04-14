// Orquestador Nexus: Sincronización Local-First (Expert 11)
// Versión Final con Parches de Seguridad para Navegador (CORS/Worker)

import { PowerSyncDatabase, Schema, Table, column, WASQLiteOpenFactory } from 'https://esm.sh/@powersync/web@1.37.1';

const POWERSYNC_URL = 'https://69ddb32f01d9355a4acaad89.powersync.journeyapps.com';

const app_saas_auth_user = new Table({
    password: column.text,
    last_login: column.text,
    is_superuser: column.integer,
    username: column.text,
    first_name: column.text,
    last_name: column.text,
    email: column.text,
    is_staff: column.integer,
    is_active: column.integer,
    date_joined: column.text,
    role: column.text,
    is_premium: column.integer,
    avatar_url: column.text,
    organization_id: column.text
});

const NEXUS_SCHEMA = new Schema({
    app_saas_auth_user
});

class PowerSyncBridge {
    constructor() {
        try {
            console.log("🛠️ Nexus: Inicializando con parches de seguridad...");
            this.db = new PowerSyncDatabase({
                schema: NEXUS_SCHEMA,
                database: {
                    dbFilename: 'nex21_master_final_stable.db'
                },
                // BANDERAS DE SEGURIDAD CRUCIALES
                flags: {
                    enableMultiTabs: false, // Evita usar SharedWorker para sincronización
                    useWebWorker: false,    // Evita usar SharedWorker para SQLite
                    externallyUnload: true  // Corrige la violación de Permissions Policy: unload
                }
            });
        } catch (e) {
            console.error("❌ Nexus: Error en inicialización.", e);
        }
    }

    async init() {
        if (!this.db) return;
        
        console.log("🚀 Nexus: Arrancando motor Local-First...");
        try {
            await this.db.init();
            
            await this.db.connect({
                endpoint: POWERSYNC_URL,
                params: {
                    "ps_development_token": "true" 
                }
            });

            console.log("✅ Nexus: ¡Sincronizado con éxito!");
            this.updateUI('connected');

        } catch (error) {
            console.error("❌ Nexus Error:", error);
            this.updateUI('error');
        }
    }

    updateUI(status) {
        const text = document.getElementById('sync-status-text');
        const icon = document.getElementById('sync-status-icon');
        
        if (text && icon) {
            if (status === 'connected') {
                icon.className = 'fas fa-circle text-success animate__animated animate__pulse';
                icon.style.filter = 'drop-shadow(0 0 5px #28a745)';
                text.innerText = "Nexus Sincronizado";
                text.style.color = "#28a745";
                text.style.fontWeight = "bold";
            } else {
                icon.className = 'fas fa-circle text-danger';
                icon.style.filter = 'drop-shadow(0 0 5px #dc3545)';
                text.innerText = "Error / Offline";
                text.style.color = "#dc3545";
                text.style.fontWeight = "bold";
            }
        }
    }
}

// Inicialización
const bridge = new PowerSyncBridge();
bridge.init();
