-- =====================================================================
-- SISTEMA DE GESTIÓN DE MANTENIMIENTO ASISTIDO POR ORDENADOR (GMAO / CMMS)
-- ARQUITECTURA DE BASE DE DATOS RELACIONAL EMPRESARIAL
-- Estándares de Referencia: ISO 14224 (Confiabilidad y Mantenimiento)
--                          ISO 55000 (Gestión de Activos Físicos)
-- Compatible con: PostgreSQL 12+ / MySQL 8.0+ / MariaDB 10.5+ / SQLite 3
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. SEGURIDAD, USUARIOS Y CONTROL DE ACCESO (RBAC)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    nivel_acceso INT NOT NULL DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE,
    telefono VARCHAR(30),
    rol_id VARCHAR(20) NOT NULL,
    cargo VARCHAR(80),
    departamento VARCHAR(80),
    es_activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS tecnicos_perfil (
    usuario_id VARCHAR(36) PRIMARY KEY,
    especialidad VARCHAR(80) NOT NULL, -- Electromecánico, Instrumentista, Refrigeración, Mecánico, Soldador
    tarifa_hora DECIMAL(10, 2) DEFAULT 0.00,
    certificaciones TEXT,
    disponible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- 2. JERARQUÍA DE ACTIVOS Y UBICACIONES TÉCNICAS (ISO 14224)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS plantas (
    id VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    contacto_planta VARCHAR(100),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS areas (
    id VARCHAR(30) PRIMARY KEY,
    planta_id VARCHAR(30) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    responsable_area VARCHAR(100),
    FOREIGN KEY (planta_id) REFERENCES plantas(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS lineas_produccion (
    id VARCHAR(30) PRIMARY KEY,
    area_id VARCHAR(30) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    centro_costo VARCHAR(50),
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS activos_equipos (
    id VARCHAR(50) PRIMARY KEY, -- Código Tag: EQ-101, COMP-01, etc.
    linea_id VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    tipo_equipo VARCHAR(80) NOT NULL, -- Compresor, Bomba, Banda, Horno, Chiller, etc.
    subensamble_principal VARCHAR(100),
    marca VARCHAR(80),
    modelo VARCHAR(80),
    numero_serie VARCHAR(80),
    año_fabricacion INT,
    criticidad VARCHAR(10) NOT NULL CHECK (criticidad IN ('Alta', 'Media', 'Baja')),
    estado_operativo VARCHAR(25) NOT NULL DEFAULT 'Operativo' CHECK (estado_operativo IN ('Operativo', 'En Falla', 'En Mantenimiento', 'Fuera de Servicio')),
    es_refrigeracion BOOLEAN DEFAULT FALSE,
    tipo_refrigerante VARCHAR(50), -- R-22, R-134a, R-410A, Amoniaco
    carga_refrigerante_kg DECIMAL(8, 2),
    potencia_kw DECIMAL(8, 2),
    voltaje_v INT,
    ubicacion_detallada VARCHAR(150),
    fecha_puesta_marcha DATE,
    costo_adquisicion DECIMAL(12, 2) DEFAULT 0.00,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (linea_id) REFERENCES lineas_produccion(id) ON DELETE RESTRICT
);

CREATE INDEX idx_activos_criticidad ON activos_equipos(criticidad);
CREATE INDEX idx_activos_estado ON activos_equipos(estado_operativo);

-- ---------------------------------------------------------------------
-- 3. PROVEEDORES, ALMACÉN Y GESTIÓN DE REPUESTOS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS proveedores (
    id VARCHAR(36) PRIMARY KEY,
    rif_nit VARCHAR(30) NOT NULL UNIQUE,
    razon_social VARCHAR(150) NOT NULL,
    contacto_nombre VARCHAR(100),
    email VARCHAR(120),
    telefono VARCHAR(30),
    direccion VARCHAR(200),
    ciudad VARCHAR(80),
    categoria VARCHAR(80), -- Repuestos Mecánicos, Eléctricos, Gases Refrigerantes, Servicios
    condicion_pago VARCHAR(50) DEFAULT 'Crédito 30 días',
    calificacion_estrellas INT DEFAULT 5 CHECK (calificacion_estrellas BETWEEN 1 AND 5),
    es_activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repuestos_materiales (
    id VARCHAR(36) PRIMARY KEY,
    codigo_articulo VARCHAR(50) NOT NULL UNIQUE, -- SKF-6205, FIL-AIR-01
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(60), -- Rodamientos, Filtros, Lubricantes, Válvulas, Sellos, Gases
    unidad_medida VARCHAR(20) NOT NULL DEFAULT 'pza', -- pza, Litros, Kg, Metros
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 2,
    stock_maximo INT NOT NULL DEFAULT 50,
    punto_reorden INT NOT NULL DEFAULT 5,
    costo_unitario DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    moneda VARCHAR(5) DEFAULT '$',
    pasillo_estante VARCHAR(50), -- Bodega A, Estante 3, Nivel 2
    proveedor_habitual_id VARCHAR(36),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_habitual_id) REFERENCES proveedores(id) ON DELETE SET NULL
);

CREATE INDEX idx_repuestos_stock ON repuestos_materiales(stock_actual, stock_minimo);

CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id VARCHAR(36) PRIMARY KEY,
    repuesto_id VARCHAR(36) NOT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN ('ENTRADA', 'SALIDA', 'AJUSTE', 'DEVOLUCION')),
    cantidad INT NOT NULL,
    stock_anterior INT NOT NULL,
    stock_resultante INT NOT NULL,
    costo_unitario_momento DECIMAL(10, 2) NOT NULL,
    referencia_origen VARCHAR(50), -- Folio de OT, Solicitud de Compra, etc.
    motivo VARCHAR(200),
    usuario_id VARCHAR(36) NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repuesto_id) REFERENCES repuestos_materiales(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- 4. SOLICITUDES DE MANTENIMIENTO INTERDEPARTAMENTALES (HELP DESK)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS solicitudes_mantenimiento (
    id VARCHAR(30) PRIMARY KEY, -- SOL-2026-001
    tipo_solicitud VARCHAR(50) NOT NULL, -- Maquinaria / Equipo, Infraestructura / Instalaciones
    urgencia VARCHAR(15) NOT NULL CHECK (urgencia IN ('Baja', 'Media', 'Alta', 'Crítica')),
    area_origen VARCHAR(100) NOT NULL,
    ubicacion_afectada VARCHAR(150) NOT NULL,
    equipo_id VARCHAR(50),
    descripcion TEXT NOT NULL,
    solicitante_id VARCHAR(36) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Aprobada', 'En Proceso', 'Rechazada', 'Cumplida')),
    motivo_rechazo TEXT,
    ot_vinculada_id VARCHAR(30),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipo_id) REFERENCES activos_equipos(id) ON DELETE SET NULL,
    FOREIGN KEY (solicitante_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- 5. PLANES DE MANTENIMIENTO PREVENTIVO Y RUTINAS PROGRAMADAS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS planes_preventivos (
    id VARCHAR(30) PRIMARY KEY, -- PLN-01, PLR-01
    equipo_id VARCHAR(50) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    frecuencia VARCHAR(20) NOT NULL CHECK (frecuencia IN ('Diario', 'Semanal', 'Quincenal', 'Mensual', 'Trimestral', 'Semestral', 'Anual')),
    dias_intervalo INT NOT NULL DEFAULT 30,
    ultima_fecha DATE NOT NULL,
    proxima_fecha DATE NOT NULL,
    es_refrigeracion BOOLEAN DEFAULT FALSE,
    tiempo_estimado_horas DECIMAL(4, 1) DEFAULT 2.0,
    instrucciones_procedimiento TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipo_id) REFERENCES activos_equipos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plan_tecnicos_asignados (
    plan_id VARCHAR(30) NOT NULL,
    usuario_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (plan_id, usuario_id),
    FOREIGN KEY (plan_id) REFERENCES planes_preventivos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS planes_historial_reprogramaciones (
    id VARCHAR(36) PRIMARY KEY,
    plan_id VARCHAR(30) NOT NULL,
    fecha_original DATE NOT NULL,
    nueva_fecha DATE NOT NULL,
    motivo_cambio TEXT NOT NULL,
    usuario_responsable_id VARCHAR(36) NOT NULL,
    registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES planes_preventivos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_responsable_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- 6. ÓRDENES DE TRABAJO (OT) - CORAZÓN OPERATIVO DEL GMAO
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ordenes_trabajo (
    id VARCHAR(30) PRIMARY KEY, -- OT-2026-001
    tipo VARCHAR(25) NOT NULL CHECK (tipo IN ('Correctivo', 'Preventivo', 'Eventual', 'Predictivo', 'Mejora')),
    prioridad VARCHAR(15) NOT NULL CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Emergencia')),
    equipo_id VARCHAR(50) NOT NULL,
    plan_preventivo_id VARCHAR(30),
    solicitud_origen_id VARCHAR(30),
    descripcion_falla_requerimiento TEXT NOT NULL,
    estado VARCHAR(25) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'En Proceso', 'En Espera Repuesto', 'Concluida', 'Cancelada')),
    fecha_emision DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_programada DATE,
    fecha_inicio TIMESTAMP,
    fecha_culminacion TIMESTAMP,
    tiempo_intervencion_horas DECIMAL(6, 2) DEFAULT 0.00,
    tiempo_parada_equipo_horas DECIMAL(6, 2) DEFAULT 0.00, -- Downtime para cálculo de Disponibilidad
    actividades_realizadas TEXT,
    diagnostico_causa_raiz TEXT,
    tecnico_acompanante_id VARCHAR(36),
    supervisor_cierre_id VARCHAR(36),
    conformidad_solicitante BOOLEAN DEFAULT FALSE,
    creado_por_id VARCHAR(36) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipo_id) REFERENCES activos_equipos(id) ON DELETE RESTRICT,
    FOREIGN KEY (plan_preventivo_id) REFERENCES planes_preventivos(id) ON DELETE SET NULL,
    FOREIGN KEY (tecnico_acompanante_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (supervisor_cierre_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (creado_por_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

CREATE INDEX idx_ot_estado ON ordenes_trabajo(estado);
CREATE INDEX idx_ot_tipo ON ordenes_trabajo(tipo);
CREATE INDEX idx_ot_equipo ON ordenes_trabajo(equipo_id);
CREATE INDEX idx_ot_fecha_prog ON ordenes_trabajo(fecha_programada);

CREATE TABLE IF NOT EXISTS ot_tecnicos_asignados (
    ot_id VARCHAR(30) NOT NULL,
    tecnico_id VARCHAR(36) NOT NULL,
    es_lider BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (ot_id, tecnico_id),
    FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo(id) ON DELETE CASCADE,
    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ot_repuestos_utilizados (
    id VARCHAR(36) PRIMARY KEY,
    ot_id VARCHAR(30) NOT NULL,
    repuesto_id VARCHAR(36),
    descripcion_libre VARCHAR(150),
    cantidad INT NOT NULL CHECK (cantidad > 0),
    costo_unitario DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    costo_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo(id) ON DELETE CASCADE,
    FOREIGN KEY (repuesto_id) REFERENCES repuestos_materiales(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ot_evidencias_fotograficas (
    id VARCHAR(36) PRIMARY KEY,
    ot_id VARCHAR(30) NOT NULL,
    tipo_foto VARCHAR(10) NOT NULL CHECK (tipo_foto IN ('ANTES', 'DURANTE', 'DESPUES')),
    ruta_almacenamiento TEXT NOT NULL, -- Ruta o URL en servidor / nube
    pie_foto VARCHAR(255),
    tomada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- 7. SOLICITUDES Y SEGUIMIENTO DE COMPRAS DE MATERIALES
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS compras_materiales (
    id VARCHAR(30) PRIMARY KEY, -- COM-01
    fecha_solicitud DATE NOT NULL,
    descripcion_material VARCHAR(200) NOT NULL,
    cantidad_solicitada INT NOT NULL CHECK (cantidad_solicitada > 0),
    cantidad_recibida INT NOT NULL DEFAULT 0 CHECK (cantidad_recibida >= 0),
    moneda VARCHAR(5) DEFAULT '$',
    precio_unitario DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    proveedor_id VARCHAR(36),
    observaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'En Trámite' CHECK (estado IN ('En Trámite', 'Parcialmente Recibido', 'Completado', 'Cancelado')),
    ot_relacionada_id VARCHAR(30),
    solicitante_id VARCHAR(36),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL,
    FOREIGN KEY (ot_relacionada_id) REFERENCES ordenes_trabajo(id) ON DELETE SET NULL,
    FOREIGN KEY (solicitante_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- ---------------------------------------------------------------------
-- 8. VISTAS SQL PARA CÁLCULO DE INDICADORES DE GESTIÓN (KPIS)
-- ---------------------------------------------------------------------

-- Vista de Disponibilidad Operativa por Equipo
CREATE OR REPLACE VIEW v_kpis_equipos AS
SELECT 
    e.id AS equipo_id,
    e.nombre AS equipo_nombre,
    e.criticidad,
    COUNT(o.id) AS total_ots,
    SUM(CASE WHEN o.estado = 'Concluida' THEN 1 ELSE 0 END) AS ots_concluidas,
    SUM(CASE WHEN o.tipo = 'Preventivo' THEN 1 ELSE 0 END) AS ots_preventivas,
    SUM(CASE WHEN o.tipo = 'Correctivo' THEN 1 ELSE 0 END) AS ots_correctivas,
    COALESCE(SUM(o.tiempo_parada_equipo_horas), 0) AS total_downtime_horas,
    COALESCE(SUM(o.tiempo_intervencion_horas), 0) AS total_intervencion_horas,
    -- MTTR: Tiempo Medio de Reparación (Horas intervención / OTs correctivas concluidas)
    CASE 
        WHEN SUM(CASE WHEN o.tipo = 'Correctivo' AND o.estado = 'Concluida' THEN 1 ELSE 0 END) > 0 
        THEN ROUND(SUM(CASE WHEN o.tipo = 'Correctivo' THEN o.tiempo_intervencion_horas ELSE 0 END) / 
                   SUM(CASE WHEN o.tipo = 'Correctivo' AND o.estado = 'Concluida' THEN 1 ELSE 0 END), 2)
        ELSE 0.00 
    END AS mttr_horas,
    -- Disponibilidad Operativa mensual estimada sobre base de 720 horas/mes
    ROUND(GREATEST(0, (720.0 - COALESCE(SUM(o.tiempo_parada_equipo_horas), 0)) / 720.0 * 100), 2) AS disponibilidad_pct
FROM activos_equipos e
LEFT JOIN ordenes_trabajo o ON e.id = o.equipo_id
GROUP BY e.id, e.nombre, e.criticidad;

-- =====================================================================
-- DATOS INICIALES (SEMILLA / SEED DATA)
-- =====================================================================

INSERT INTO roles (id, nombre, descripcion, nivel_acceso) VALUES
('ROL-GER', 'Gerente', 'Jefe de Mantenimiento / Supervisor con acceso total', 10),
('ROL-TEC', 'Tecnico', 'Técnico de campo ejecutor de órdenes de trabajo', 5),
('ROL-SOL', 'Solicitante', 'Usuario de producción que genera solicitudes de servicio', 1);

INSERT INTO usuarios (id, username, password_hash, nombre_completo, email, rol_id, cargo, departamento) VALUES
('u1', 'admin', '1234', 'Ing. Carlos Mendoza', 'cmendoza@empresa.com', 'ROL-GER', 'Jefe de Mantenimiento', 'Mantenimiento'),
('u2', 'tecnico1', '1234', 'Juan Pérez (Electromecánico)', 'jperez@empresa.com', 'ROL-TEC', 'Técnico Senior', 'Mantenimiento'),
('u3', 'tecnico2', '1234', 'Miguel Torres (Instrumentista)', 'mtorres@empresa.com', 'ROL-TEC', 'Técnico Especialista', 'Mantenimiento'),
('u4', 'solicitante1', '1234', 'Roberto Gómez (Jefe Producción)', 'rgomez@empresa.com', 'ROL-SOL', 'Jefe de Turno', 'Producción');

INSERT INTO proveedores (id, rif_nit, razon_social, contacto_nombre, email, telefono, categoria) VALUES
('PRV-01', 'J-12345678-0', 'Suministros Industriales SKF C.A.', 'Marcos Rivas', 'ventas@skfsuministros.com', '+58 212-5551234', 'Rodamientos y Sellos'),
('PRV-02', 'J-87654321-9', 'Gases & Refrigeración Integral S.A.', 'Laura Morales', 'contacto@refrigeracionintegral.com', '+58 241-7778899', 'Refrigeración y Climatización');
