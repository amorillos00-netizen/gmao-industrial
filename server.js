/**
 * GMAO Industrial Pro - Servidor Web & API REST
 * Permite alojar la aplicación en una red local (Wi-Fi de Planta / LAN) o en un servidor en la nube (VPS).
 * 
 * Requisitos: Node.js 14+
 * Instalación:
 *   npm init -y
 *   npm install express cors compression
 * Ejecución:
 *   node server.js
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const compression = require('compression');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'gmao_database.json');

// Middlewares
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '50mb' })); // Soporta fotos de intervenciones
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Servir la aplicación cliente (frontend)
app.use(express.static(path.join(__dirname)));

// Función auxiliar para leer base de datos persistente
function readData() {
    try {
        if (!fs.existsSync(DATA_FILE)) {
            // Si no existe, creamos archivo inicial vacío o con semilla
            fs.writeFileSync(DATA_FILE, JSON.stringify({}, null, 2), 'utf-8');
        }
        const content = fs.readFileSync(DATA_FILE, 'utf-8');
        return JSON.parse(content || '{}');
    } catch (err) {
        console.error("Error al leer la base de datos:", err);
        return {};
    }
}

// Función auxiliar para guardar datos
function writeData(data) {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
        return true;
    } catch (err) {
        console.error("Error al guardar la base de datos:", err);
        return false;
    }
}

// --- ENDPOINTS DE LA API REST ---

// 1. Obtener estado completo sincronizado
app.get('/api/sync', (req, res) => {
    const data = readData();
    res.json({ success: true, data });
});

// 2. Guardar estado completo sincronizado
app.post('/api/sync', (req, res) => {
    const payload = req.body;
    if (!payload || typeof payload !== 'object') {
        return res.status(400).json({ success: false, message: 'Datos inválidos' });
    }
    const ok = writeData(payload);
    if (ok) {
        res.json({ success: true, message: 'Datos sincronizados en el servidor con éxito' });
    } else {
        res.status(500).json({ success: false, message: 'Error al persistir en disco' });
    }
});

// 3. Health check para monitores de infraestructura
app.get('/api/health', (req, res) => {
    res.json({ status: 'UP', timestamp: new Date().toISOString() });
});

// Ruta comodín para SPA
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Iniciar servidor escuchando en todas las interfaces de red (0.0.0.0)
app.listen(PORT, '0.0.0.0', () => {
    console.log(`=================================================================`);
    console.log(`🚀 GMAO Industrial Pro iniciado con éxito.`);
    console.log(`   Acceso Local en esta máquina: http://localhost:${PORT}`);
    console.log(`   Acceso desde Celulares/Tablets (Red LAN/Wi-Fi):`);
    console.log(`   -> Averigüe la IP de esta máquina (ej: ipconfig) y abra:`);
    console.log(`      http://<IP-DE-ESTA-MAQUINA>:${PORT}`);
    console.log(`=================================================================`);
});
