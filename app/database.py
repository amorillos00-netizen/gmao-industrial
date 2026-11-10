"""
Capa de Persistencia de Base de Datos Relacional
Compatible con SQLite 3 (con WAL y claves foráneas activadas) y extensible a PostgreSQL/MySQL.
"""
import sqlite3
import json
import uuid
from datetime import datetime
from contextlib import contextmanager
from app.config import DB_PATH, JSON_BACKUP_PATH

def init_db():
    """Inicializa el esquema relacional e inserta los datos semilla si la base está vacía."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Tablas Maestras de Seguridad y Usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            nivel_acceso INTEGER NOT NULL DEFAULT 1
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            email TEXT,
            rol_id TEXT NOT NULL,
            cargo TEXT,
            departamento TEXT,
            FOREIGN KEY (rol_id) REFERENCES roles(id)
        );
        """)

        # 2. Activos y Ubicaciones Técnicas (ISO 14224)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activos_equipos (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            planta TEXT NOT NULL,
            linea TEXT NOT NULL,
            subensamble TEXT DEFAULT 'General',
            criticidad TEXT NOT NULL CHECK(criticidad IN ('Alta', 'Media', 'Baja')),
            status TEXT NOT NULL DEFAULT 'Operativo' CHECK(status IN ('Operativo', 'En Mantenimiento', 'Fuera de Servicio')),
            es_refrigeracion BOOLEAN DEFAULT 0,
            tipo_refrigerante TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Proveedores y Repuestos de Almacén
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id TEXT PRIMARY KEY,
            rif TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT,
            email TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS repuestos_materiales (
            id TEXT PRIMARY KEY,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 2,
            unidad_medida TEXT NOT NULL DEFAULT 'pza',
            costo_unitario REAL NOT NULL DEFAULT 0.0,
            proveedor_id TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        );
        """)

        # 4. Solicitudes Interdepartamentales (Helpdesk de Averías)
        # Estados requeridos estrictamente: 'Aprobada', 'En espera de materiales', 'En proceso', 'Culminada'
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_mantenimiento (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            urgencia TEXT NOT NULL,
            area TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            solicitante TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aprobada' CHECK(status IN ('Aprobada', 'En espera de materiales', 'En proceso', 'Culminada')),
            ot_vinculada TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Planes de Mantenimiento Preventivo (Cronograma Anual)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS planes_preventivos (
            id TEXT PRIMARY KEY,
            equipo_id TEXT NOT NULL,
            nombre TEXT NOT NULL,
            frecuencia TEXT NOT NULL,
            frecuencia_tipo TEXT DEFAULT 'meses',
            frecuencia_valor INTEGER DEFAULT 1,
            ultima_fecha TEXT NOT NULL,
            proxima_fecha TEXT NOT NULL,
            tecnicos_ids TEXT,
            es_refrigeracion BOOLEAN DEFAULT 0,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipo_id) REFERENCES activos_equipos(id)
        );
        """)

        # 6. Órdenes de Trabajo (OT)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes_trabajo (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            equipo_id TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            tecnicos_ids TEXT,
            tecnico_acompanante TEXT,
            fecha_asignacion TEXT NOT NULL,
            fecha_programada TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            status TEXT NOT NULL DEFAULT 'Abierta' CHECK(status IN ('Abierta', 'En Progreso', 'En Pausa', 'Concluida', 'Completada', 'Cancelada')),
            actividades TEXT,
            tiempo_intervencion REAL DEFAULT 0.0,
            tiempo_parada REAL DEFAULT 0.0,
            foto_antes TEXT,
            foto_despues TEXT,
            repuestos_usados TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipo_id) REFERENCES activos_equipos(id)
        );
        """)

        # 7. Seguimiento de Compras de Materiales
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras_materiales (
            id TEXT PRIMARY KEY,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cant_solicitada INTEGER NOT NULL,
            cant_recibida INTEGER NOT NULL DEFAULT 0,
            moneda TEXT DEFAULT '$',
            precio REAL NOT NULL DEFAULT 0.0,
            proveedor_id TEXT,
            observaciones TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        );
        """)

        # 8. Módulo SSL: Solicitudes de Condiciones Inseguras (Seguridad y Salud Laboral)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes_ssl (
            id TEXT PRIMARY KEY,
            codigo TEXT UNIQUE,
            fecha_hora TEXT NOT NULL,
            area TEXT NOT NULL,
            ubicacion TEXT NOT NULL,
            equipo_id TEXT,
            nivel_riesgo TEXT NOT NULL CHECK(nivel_riesgo IN ('Bajo', 'Medio', 'Alto', 'Crítico')),
            descripcion TEXT NOT NULL,
            accion_propuesta TEXT,
            solicitante_id TEXT,
            solicitante_nombre TEXT NOT NULL,
            foto_evidencia TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendiente' CHECK(status IN ('Pendiente', 'En Corrección', 'Corregida', 'Desestimada')),
            fecha_correccion TEXT,
            ot_vinculada TEXT,
            observaciones_cierre TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 9. Motor de Notificaciones por Roles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id TEXT PRIMARY KEY,
            usuario_id TEXT,
            rol_destino TEXT,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'info',
            leido BOOLEAN DEFAULT 0,
            fecha_hora TEXT NOT NULL,
            enlace_tipo TEXT,
            enlace_id TEXT,
            activa BOOLEAN DEFAULT 1,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 10. Configuración del Sistema y Parámetros Operativos (MTTR, Metas, Alertas)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_sistema (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL,
            descripcion TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 11. Módulo de Seguimiento de Equipos en Taller Externo (Soporta activos registrados o manuales)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos_taller_externo (
            id TEXT PRIMARY KEY,
            equipo_id TEXT NOT NULL,
            proveedor_id TEXT,
            proveedor_nombre TEXT NOT NULL,
            fecha_salida TEXT NOT NULL,
            fecha_estimada_retorno TEXT,
            fecha_retorno_real TEXT,
            motivo_servicio TEXT NOT NULL,
            costo_estimado REAL DEFAULT 0.0,
            costo_final REAL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'En diagnóstico' CHECK(status IN ('En diagnóstico', 'En reparación', 'Esperando repuestos', 'Listo para retiro', 'Recibido en Planta')),
            condicion_recepcion TEXT,
            recibido_por TEXT,
            observaciones TEXT,
            es_manual BOOLEAN DEFAULT 0,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        );
        """)

        # 12. Control de Salida y Despacho de Materiales / Repuestos (Rol Almacenista)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS salidas_materiales (
            id TEXT PRIMARY KEY,
            fecha TEXT NOT NULL,
            ot_id TEXT,
            solicitud_id TEXT,
            repuesto_id TEXT NOT NULL,
            repuesto_nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            despachado_por TEXT NOT NULL,
            receptor TEXT NOT NULL,
            observaciones TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repuesto_id) REFERENCES repuestos_materiales(id),
            FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo(id) ON DELETE SET NULL
        );
        """)

        # Migraciones dinámicas si las columnas no existen aún
        ensure_columns(cursor)

        # 11. Insertar semilla inicial si la base está nueva o faltan roles
        seed_initial_data(cursor)
            
        conn.commit()

def ensure_columns(cursor):
    try:
        cursor.execute("INSERT OR IGNORE INTO roles (id, nombre, descripcion, nivel_acceso) VALUES ('ROL-COM', 'Departamento de Compras', 'Gestión, cotización y actualización de estatus de solicitudes de materiales', 6);")
        cursor.execute("""
            INSERT INTO usuarios (id, username, password_hash, nombre_completo, email, rol_id, cargo, departamento)
            VALUES ('u_compras', 'compras1', '1234', 'Lic. Elena Ramos (Compras)', 'eramos@empresa.com', 'ROL-COM', 'Encargada de Compras', 'Departamento de Compras')
            ON CONFLICT(username) DO UPDATE SET rol_id = 'ROL-COM', cargo = 'Encargada de Compras', departamento = 'Departamento de Compras';
        """)
        cursor.execute("UPDATE usuarios SET rol_id = 'ROL-ALM' WHERE username = 'almacenista';")
        cursor.execute("PRAGMA table_info(compras_materiales);")
        cols = [c[1] for c in cursor.fetchall()]
        if 'status' not in cols:
            cursor.execute("ALTER TABLE compras_materiales ADD COLUMN status TEXT DEFAULT 'Pendiente';")
        if 'creado_por' not in cols:
            cursor.execute("ALTER TABLE compras_materiales ADD COLUMN creado_por TEXT DEFAULT 'Jefe de Mantenimiento';")
    except Exception as e:
        pass
    """Añade columnas a tablas existentes en caso de actualización sin perder datos."""
    try:
        cursor.execute("PRAGMA table_info(planes_preventivos);")
        cols = [c[1] for c in cursor.fetchall()]
        if 'frecuencia_tipo' not in cols:
            cursor.execute("ALTER TABLE planes_preventivos ADD COLUMN frecuencia_tipo TEXT DEFAULT 'meses';")
        if 'frecuencia_valor' not in cols:
            cursor.execute("ALTER TABLE planes_preventivos ADD COLUMN frecuencia_valor INTEGER DEFAULT 1;")
        if 'status' not in cols:
            cursor.execute("ALTER TABLE planes_preventivos ADD COLUMN status TEXT DEFAULT 'Pendiente';")
    except Exception as e:
        pass

    try:
        cursor.execute("PRAGMA table_info(ordenes_trabajo);")
        cols = [c[1] for c in cursor.fetchall()]
        if 'plan_id' not in cols:
            cursor.execute("ALTER TABLE ordenes_trabajo ADD COLUMN plan_id TEXT;")
    except Exception as e:
        pass

    try:
        cursor.execute("PRAGMA table_info(notificaciones);")
        cols = [c[1] for c in cursor.fetchall()]
        if 'activa' not in cols:
            cursor.execute("ALTER TABLE notificaciones ADD COLUMN activa BOOLEAN DEFAULT 1;")
    except Exception as e:
        pass

    for table in ['planes_preventivos', 'solicitudes_mantenimiento', 'ordenes_trabajo', 'activos_equipos', 'proveedores', 'repuestos_materiales', 'compras_materiales', 'equipos_taller_externo']:
        try:
            cursor.execute(f"PRAGMA table_info({table});")
            cols = [c[1] for c in cursor.fetchall()]
            if 'updated_at' not in cols:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at TEXT;")
        except Exception as e:
            pass

    # Migración de tabla equipos_taller_externo para permitir equipos manuales sin restricción de FK
    try:
        cursor.execute("PRAGMA foreign_key_list(equipos_taller_externo);")
        fks = cursor.fetchall()
        has_activo_fk = any(fk[2] == 'activos_equipos' for fk in fks)
        if has_activo_fk:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipos_taller_externo_temp (
                id TEXT PRIMARY KEY,
                equipo_id TEXT NOT NULL,
                proveedor_id TEXT,
                proveedor_nombre TEXT NOT NULL,
                fecha_salida TEXT NOT NULL,
                fecha_estimada_retorno TEXT,
                fecha_retorno_real TEXT,
                motivo_servicio TEXT NOT NULL,
                costo_estimado REAL DEFAULT 0.0,
                costo_final REAL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'En diagnóstico',
                condicion_recepcion TEXT,
                recibido_por TEXT,
                observaciones TEXT,
            status TEXT NOT NULL DEFAULT 'Pendiente',
                es_manual BOOLEAN DEFAULT 0,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
            );
            """)
            cursor.execute("""
            INSERT OR REPLACE INTO equipos_taller_externo_temp (
                id, equipo_id, proveedor_id, proveedor_nombre, fecha_salida, fecha_estimada_retorno,
                fecha_retorno_real, motivo_servicio, costo_estimado, costo_final, status,
                condicion_recepcion, recibido_por, observaciones, creado_en, updated_at
            )
            SELECT id, equipo_id, proveedor_id, proveedor_nombre, fecha_salida, fecha_estimada_retorno,
                   fecha_retorno_real, motivo_servicio, costo_estimado, costo_final, status,
                   condicion_recepcion, recibido_por, observaciones, creado_en, updated_at
            FROM equipos_taller_externo;
            """)
            cursor.execute("DROP TABLE equipos_taller_externo;")
            cursor.execute("ALTER TABLE equipos_taller_externo_temp RENAME TO equipos_taller_externo;")
    except Exception as e:
        pass

    # Reconciliación automática de estados concluidos y limpieza de notificaciones huérfanas
    try:
        cursor.execute("""
            UPDATE solicitudes_ssl
            SET status = 'Corregida', fecha_correccion = '2026-10-29 11:00'
            WHERE ot_vinculada IN (SELECT id FROM ordenes_trabajo WHERE status IN ('Concluida', 'Completada'))
            AND status NOT IN ('Corregida', 'Desestimada');
        """)
        cursor.execute("""
            UPDATE solicitudes_mantenimiento
            SET status = 'Culminada'
            WHERE ot_vinculada IN (SELECT id FROM ordenes_trabajo WHERE status IN ('Concluida', 'Completada'))
            AND status != 'Culminada';
        """)
        cursor.execute("""
            UPDATE notificaciones
            SET leido = 1
            WHERE (enlace_tipo = 'solicitud' AND enlace_id IN (SELECT id FROM solicitudes_mantenimiento WHERE status = 'Culminada'))
               OR (enlace_tipo = 'ssl' AND enlace_id IN (SELECT id FROM solicitudes_ssl WHERE status IN ('Corregida', 'Desestimada')));
        """)
    except Exception as e:
        pass

def seed_initial_data(cursor):
    """Carga los datos industriales de prueba y roles autorizados."""
    # Roles
    roles = [
        ('ROL-GER', 'Gerente', 'Jefe de Mantenimiento / Supervisor con control total', 10),
        ('ROL-TEC', 'Tecnico', 'Técnico ejecutor de campo (Móvil/Tablet)', 5),
        ('ROL-SOL', 'Solicitante', 'Operador o Supervisor de Producción', 1),
        ('ROL-SSL', 'Jefe SSL', 'Responsable de Seguridad, Salud y Medio Ambiente Laboral', 7),
        ('ROL-ALM', 'Almacenista', 'Gestión de inventario, recepción y salida de repuestos/materiales', 4),
        ('ROL-COM', 'Departamento de Compras', 'Gestión, cotización y actualización de estatus de solicitudes de materiales', 6)
    ]
    cursor.executemany("INSERT OR IGNORE INTO roles (id, nombre, descripcion, nivel_acceso) VALUES (?, ?, ?, ?)", roles)

    # Usuarios productivos autorizados
    usuarios = [
        ('u1', 'admin', '1234', 'Ing. Carlos Mendoza (Jefe Mantenimiento)', 'cmendoza@empresa.com', 'ROL-GER', 'Jefe de Mantenimiento', 'Mantenimiento'),
        ('u2', 'tecnico1', '1234', 'Juan Pérez (Electromecánico)', 'jperez@empresa.com', 'ROL-TEC', 'Técnico Senior', 'Mantenimiento'),
        ('u3', 'tecnico2', '1234', 'Miguel Torres (Instrumentista)', 'mtorres@empresa.com', 'ROL-TEC', 'Técnico Especialista', 'Mantenimiento'),
        ('u4', 'solicitante1', '1234', 'Roberto Gómez (Jefe Producción)', 'rgomez@empresa.com', 'ROL-SOL', 'Jefe de Turno', 'Producción'),
        ('u5', 'jefessl', '1234', 'Ing. Argenis Morillo (Jefe SSL)', 'amorillo@empresa.com', 'ROL-SSL', 'Jefe de Seguridad y Salud Laboral', 'Seguridad y Salud'),
        ('u6', 'gerente_planta', '1234', 'Ing. Roberto Navarro (Gerente de Planta)', 'rnavarro@empresa.com', 'ROL-GER', 'Gerente de Planta', 'Gerencia General'),
        ('u7', 'almacenista', '1234', 'Pedro Ramírez (Almacenista)', 'pramirez@empresa.com', 'ROL-ALM', 'Almacenista Principal', 'Almacén y Suministros'),
        ('u8', 'compras1', '1234', 'Lic. Elena Ramos (Compras)', 'eramos@empresa.com', 'ROL-COM', 'Encargada de Compras', 'Departamento de Compras')
    ]
    cursor.executemany("INSERT OR IGNORE INTO usuarios (id, username, password_hash, nombre_completo, email, rol_id, cargo, departamento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", usuarios)

    # Configuración del Sistema Semilla (Umbrales KPI y Alertas)
    configuraciones = [
        ('mttr_target_hours', '2.0', 'Umbral mínimo de referencia o meta de MTTR en horas'),
        ('availability_target_pct', '95.0', 'Meta de disponibilidad de planta en porcentaje'),
        ('preventive_alert_days', '5', 'Días de anticipación para disparar alertas de mantenimiento preventivo')
    ]
    cursor.executemany("INSERT OR IGNORE INTO configuracion_sistema (clave, valor, descripcion) VALUES (?, ?, ?)", configuraciones)

    # Proveedores
    proveedores = [
        ('PRV-01', 'J-12345678-0', 'Suministros Industriales SKF C.A.', 'Rodamientos y Sellos', 'Marcos Rivas', '+58 212-5551234', 'ventas@skfsuministros.com'),
        ('PRV-02', 'J-87654321-9', 'Gases & Refrigeración Integral S.A.', 'Refrigeración y Climatización', 'Laura Morales', '+58 241-7778899', 'contacto@refrigeracionintegral.com'),
        ('PRV-03', 'J-55443322-1', 'ElectroMotores & Automatización del Centro', 'Electricidad e Instrumentación', 'Ing. David Salazar', '+58 241-9988776', 'ventas@electromotores.com')
    ]
    cursor.executemany("INSERT OR IGNORE INTO proveedores (id, rif, nombre, categoria, contacto, telefono, email) VALUES (?, ?, ?, ?, ?, ?, ?)", proveedores)

    # Activos según planta de SALTYSNACK TUYERO C.A.
    equipos = [
        ('EQ-101', 'Compresor de Aire Tornillo Principal', 'Planta Central', 'Servicios Generales', 'Unidad de Compresión', 'Alta', 'Operativo', 0, None),
        ('EQ-102', 'Bomba Centrífuga Alimentadora #1', 'Planta Central', 'Línea de Envasado 1', 'Motor y Sello Mecánico', 'Alta', 'Operativo', 0, None),
        ('EQ-103', 'Cinta Transportadora Principal', 'Planta Central', 'Empaque Final', 'Reductor y Banda', 'Media', 'Operativo', 0, None),
        ('EQ-104', 'Horno Industrial de Curado', 'Planta Norte', 'Línea de Pintura', 'Quemadores', 'Baja', 'Operativo', 0, None),
        ('EQ-105', 'Sistema de Refrigeración Industrial R-22', 'Planta Norte', 'Cadena de Frío', 'Compresor y Condensador', 'Alta', 'Operativo', 1, 'R-22'),
        ('AC-201', 'Aire Acondicionado Central Sala de Control', 'Planta Norte', 'Climatización', 'Evaporador / Compresor', 'Media', 'Operativo', 1, 'R-410A'),
        ('B01', 'Extrusora doble tornillo 1', 'Planta Central', 'Producción Snacks', 'Cabezal y Reductor', 'Alta', 'Operativo', 0, None),
        ('B02', 'Extrusora doble tornillo 2', 'Planta Central', 'Producción Snacks', 'Cabezal y Reductor', 'Alta', 'Operativo', 0, None)
    ]
    cursor.executemany("INSERT OR IGNORE INTO activos_equipos (id, nombre, planta, linea, subensamble, criticidad, status, es_refrigeracion, tipo_refrigerante) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", equipos)

    # Repuestos
    repuestos = [
        ('REP-01', 'SKF-6205', 'Rodamiento Rígido 6205 2RS', 15, 5, 'pza', 14.50, 'PRV-01'),
        ('REP-02', 'FIL-AIR-01', 'Filtro de Aire Industrial Compresor', 3, 2, 'pza', 48.00, 'PRV-01'),
        ('REP-03', 'ACE-IND-68', 'Aceite Sintético ISO VG 68', 50, 20, 'Litros', 8.50, 'PRV-01'),
        ('REP-04', 'GAS-R22', 'Cilindro Gas Refrigerante R-22 13.6kg', 2, 1, 'Cilindro', 160.00, 'PRV-02'),
        ('REP-05', 'SEL-MEC-32', 'Sello Mecánico Bomba 1.5 pulg', 2, 2, 'pza', 85.00, 'PRV-01'),
        ('REP-06', 'KIT-JUN-01', 'Kit de juntas / Limpiador mordazas', 8, 2, 'pza', 32.00, 'PRV-01')
    ]
    cursor.executemany("INSERT OR IGNORE INTO repuestos_materiales (id, codigo, nombre, stock, stock_minimo, unidad_medida, costo_unitario, proveedor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", repuestos)

    # Planes Preventivos
    planes = [
        ('PLN-01', 'EQ-101', 'Mantenimiento de Filtros y Lubricación', 'Mensual', 'meses', 1, '2026-10-05', '2026-11-05', json.dumps(['u2']), 0),
        ('PLN-02', 'EQ-102', 'Inspección de Vibración y Sellos', 'Quincenal', 'dias', 15, '2026-10-16', '2026-10-31', json.dumps(['u3']), 0),
        ('PLN-03', 'B01', 'Mantenimiento Preventivo Semanal Extrusora', 'Semanal', 'semanas', 1, '2026-10-25', '2026-11-01', json.dumps(['u2', 'u3']), 0),
        ('PLR-01', 'EQ-105', 'Limpieza de Condensadores y Revisión Presión R-22', 'Mensual', 'meses', 1, '2026-10-02', '2026-11-02', json.dumps(['u2']), 1),
        ('PLR-02', 'AC-201', 'Mantenimiento Preventivo Unidades Manejadoras AC', 'Trimestral', 'meses', 3, '2026-08-10', '2026-11-10', json.dumps(['u3']), 1)
    ]
    cursor.executemany("INSERT OR IGNORE INTO planes_preventivos (id, equipo_id, nombre, frecuencia, frecuencia_tipo, frecuencia_valor, ultima_fecha, proxima_fecha, tecnicos_ids, es_refrigeracion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", planes)

    # Solicitudes Interdepartamentales (estados: 'Aprobada', 'En espera de materiales', 'En proceso', 'Culminada')
    solicitudes = [
        ('SOL-2026-001', 'Maquinaria / Equipo', 'Alta', 'Producción - Envasado', 'Cinta Transportadora #3', 'Fuga de aceite en reductor principal y vibración anormal.', 'Roberto Gómez (Jefe Producción)', '2026-10-29 10:15', 'Aprobada', 'OT-2026-001'),
        ('SOL-2026-002', 'Infraestructura', 'Media', 'Almacén Central', 'Portón Eléctrico Principal', 'Sensor fin de carrera descalibrado, apertura incompleta.', 'Roberto Gómez (Jefe Producción)', '2026-11-01 08:30', 'En proceso', None),
        ('SOL-2026-003', 'Maquinaria / Equipo', 'Baja', 'Línea de Envasado 1', 'Bomba Centrífuga #1', 'Revisión preventiva de sello mecánico por goteo leve.', 'Roberto Gómez (Jefe Producción)', '2026-11-02 14:00', 'En espera de materiales', None)
    ]
    cursor.executemany("INSERT OR IGNORE INTO solicitudes_mantenimiento (id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status, ot_vinculada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", solicitudes)

    # OTs (conforme matriz control de OT SALTYSNACK TUYERO C.A.)
    ots = [
        ('OT-2026-001', 'Preventivo', 'Alta', 'EQ-103', 'Ajuste de mordazas y alineación de banda empaque.', json.dumps(['u2']), 'u3', '2026-10-15', '2026-10-20', '2026-10-20T08:00', '2026-10-20T08:45', 'Concluida', 'Se calibraron mordazas térmicas y se cambió kit de juntas limpiadoras. Operativo sin novedad.', 0.75, 0.75, '', '', json.dumps([{'name': 'Kit de juntas / Limpiador mordazas', 'cant': 1, 'costo': 32.00}])),
        ('OT-2026-002', 'Correctivo', 'Alta', 'EQ-101', 'Revisión por caída de presión en línea de aire comprimido.', json.dumps(['u2', 'u3']), 'u3', '2026-10-25', '2026-10-25', '2026-10-25T09:00', '2026-10-25T11:30', 'Concluida', 'Reemplazo de válvula solenoide y purga de condensados.', 2.5, 2.5, '', '', json.dumps([{'name': 'Filtro de Aire Industrial Compresor', 'cant': 1, 'costo': 48.00}])),
        ('OT-2026-003', 'Preventivo', 'Media', 'EQ-102', 'Inspección de vibraciones y lubricación de rodamientos bomba.', json.dumps(['u3']), '', '2026-11-01', '2026-11-02', '', '', 'En Proceso', 'Pendiente completar medición de termografía.', 0.0, 0.0, '', '', json.dumps([]))
    ]
    cursor.executemany("INSERT OR IGNORE INTO ordenes_trabajo (id, tipo, prioridad, equipo_id, descripcion, tecnicos_ids, tecnico_acompanante, fecha_asignacion, fecha_programada, fecha_inicio, fecha_fin, status, actividades, tiempo_intervencion, tiempo_parada, foto_antes, foto_despues, repuestos_usados) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ots)

    # Solicitudes SSL Iniciales
    solicitudes_ssl = [
        ('SSL-2026-001', 'COND-001', '2026-10-28 09:30', 'Planta Central - Envasado', 'Cinta Transportadora Principal', 'EQ-103', 'Alto', 'Falta resguardo de seguridad en polea motriz, riesgo de atrapamiento mecánico para operadores.', 'Instalar guarda perimetral de policarbonato o malla metálica con enclavamiento.', 'u5', 'Ing. Argenis Morillo (Jefe SSL)', '', 'Corregida', '2026-10-29 11:00', 'OT-2026-001', 'OT vinculada OT-2026-001 concluida. Resguardo instalado.')
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO solicitudes_ssl (
        id, codigo, fecha_hora, area, ubicacion, equipo_id, nivel_riesgo, descripcion, accion_propuesta, solicitante_id, solicitante_nombre, foto_evidencia, status, fecha_correccion, ot_vinculada, observaciones_cierre
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, solicitudes_ssl)

    # Notificaciones Semilla (items culminados inician leídos para evitar badges residuales)
    notificaciones = [
        ('NOTIF-01', 'u1', 'Gerente', 'Nueva Solicitud Interdepartamental', 'Producción reportó falla en Envasado (SOL-2026-001)', 'warning', 1, '2026-10-29 10:15', 'solicitud', 'SOL-2026-001'),
        ('NOTIF-02', 'u1', 'Gerente', 'Condición Insegura Reportada (SSL)', 'Ing. Argenis Morillo reportó condición de Alto Riesgo en Envasado', 'urgent', 1, '2026-10-28 09:35', 'ssl', 'SSL-2026-001'),
        ('NOTIF-03', 'u2', 'Tecnico', 'Nueva OT Asignada', 'Se le asignó la OT-2026-001: Mantenimiento de mordazas', 'info', 1, '2026-10-20 07:30', 'ot', 'OT-2026-001'),
        ('NOTIF-04', 'u5', 'Jefe SSL', 'Actualización de Condición SSL', 'La condición SSL-2026-001 ha sido mitigada y corregida', 'success', 1, '2026-10-29 11:00', 'ssl', 'SSL-2026-001')
    ]
    cursor.executemany("INSERT OR IGNORE INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, leido, fecha_hora, enlace_tipo, enlace_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", notificaciones)

    # Compras
    compras = [
        ('COM-01', '2026-10-15', 'Rodamiento Rígido SKF 6205', 10, 10, '$', 14.50, 'PRV-01', 'Entregado conforme en almacén'),
        ('COM-02', '2026-10-25', 'Gas Refrigerante R-22 (Cilindro)', 2, 1, '$', 160.00, 'PRV-02', 'Pendiente entrega de 1 cilindro adicional')
    ]
    cursor.executemany("INSERT OR IGNORE INTO compras_materiales (id, fecha, descripcion, cant_solicitada, cant_recibida, moneda, precio, proveedor_id, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", compras)

    # Equipos en Taller Externo Semilla
    equipos_externos = [
        ('EXT-2026-001', 'EQ-102', 'PRV-03', 'ElectroMotores & Automatización del Centro', '2026-11-01', '2026-11-15', None, 'Rebobinado de motor trifásico 15HP y balanceo dinámico de rotor', 350.00, 0.0, 'En reparación', None, None, 'Enviado por falla de aislamiento térmico tras sobrecarga.')
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO equipos_taller_externo (
        id, equipo_id, proveedor_id, proveedor_nombre, fecha_salida, fecha_estimada_retorno,
        fecha_retorno_real, motivo_servicio, costo_estimado, costo_final, status,
        condicion_recepcion, recibido_por, observaciones
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, equipos_externos)

    # Salidas de Materiales Semilla
    salidas = [
        ('SAL-2026-001', '2026-10-20 08:30', 'OT-2026-001', 'SOL-2026-001', 'REP-06', 'Kit de juntas / Limpiador mordazas', 1, 'Pedro Ramírez (Almacenista)', 'Juan Pérez (Técnico)', 'Despacho para mantenimiento preventivo de mordazas')
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO salidas_materiales (
        id, fecha, ot_id, solicitud_id, repuesto_id, repuesto_nombre, cantidad,
        despachado_por, receptor, observaciones
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, salidas)

_columns_checked = False

@contextmanager
def get_db():
    """Generador de contexto para conexiones seguras con WAL, Claves Foráneas y timeout de concurrencia optimizado."""
    global _columns_checked
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    if not _columns_checked:
        try:
            cur = conn.cursor()
            ensure_columns(cur)
            conn.commit()
            _columns_checked = True
        except Exception:
            pass
    try:
        yield conn
    finally:
        conn.close()
