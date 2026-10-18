import re
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Set

import os

# Cargar variables del archivo .env si existe en la carpeta backend o raiz
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
]

for env_path in env_paths:
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        break

DB_CONN_PARAMS = {
    "dbname": os.getenv("DB_NAME", "bimeh"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}
if os.getenv("DB_SSLMODE"):
    DB_CONN_PARAMS["sslmode"] = os.getenv("DB_SSLMODE")



class CursorWrapper:
    def __init__(self, cursor, conn_wrapper=None):
        self._cursor = cursor
        self._conn_wrapper = conn_wrapper
        
    def execute(self, query, vars=None):
        if isinstance(query, str):
            query = query.replace("strftime('%m', fecha)", "to_char(to_date(fecha, 'YYYY-MM-DD'), 'MM')")
            query = query.replace("strftime('%d', fecha)", "to_char(to_date(fecha, 'YYYY-MM-DD'), 'DD')")
            query = query.replace("strftime('%m', r.fecha)", "to_char(to_date(r.fecha, 'YYYY-MM-DD'), 'MM')")
            query = query.replace("strftime('%d', r.fecha)", "to_char(to_date(r.fecha, 'YYYY-MM-DD'), 'DD')")
            query = query.replace('?', '%s')
        try:
            return self._cursor.execute(query, vars)
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            if self._conn_wrapper:
                self._conn_wrapper.reconnect()
                self._cursor = self._conn_wrapper._conn.cursor()
                return self._cursor.execute(query, vars)
            raise e
        
    def fetchone(self):
        try:
            return self._cursor.fetchone()
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            if self._conn_wrapper:
                self._conn_wrapper.reconnect()
                self._cursor = self._conn_wrapper._conn.cursor()
                return self._cursor.fetchone()
            raise e
        
    def fetchall(self):
        try:
            return self._cursor.fetchall()
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            if self._conn_wrapper:
                self._conn_wrapper.reconnect()
                self._cursor = self._conn_wrapper._conn.cursor()
                return self._cursor.fetchall()
            raise e
        
    def __getattr__(self, name):
        return getattr(self._cursor, name)

class ConnectionWrapper:
    def __init__(self, conn=None, conn_params=None):
        self._conn_params = conn_params or DB_CONN_PARAMS
        self._conn = conn if conn else psycopg2.connect(**self._conn_params)
        self._conn.cursor_factory = psycopg2.extras.DictCursor
        
    def reconnect(self):
        try:
            if self._conn and not self._conn.closed:
                self._conn.close()
        except Exception:
            pass
        self._conn = psycopg2.connect(**self._conn_params)
        self._conn.cursor_factory = psycopg2.extras.DictCursor

    def cursor(self, *args, **kwargs):
        try:
            if self._conn.closed:
                self.reconnect()
            cursor = self._conn.cursor(*args, **kwargs)
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.reconnect()
            cursor = self._conn.cursor(*args, **kwargs)
        return CursorWrapper(cursor, self)
        
    def commit(self):
        try:
            return self._conn.commit()
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.reconnect()
            return self._conn.commit()
        
    def rollback(self):
        try:
            return self._conn.rollback()
        except Exception:
            pass
        
    def close(self):
        try:
            return self._conn.close()
        except Exception:
            pass
        
    def execute(self, query, vars=None):
        if "PRAGMA" in query:
            return None
        cursor = self.cursor()
        cursor.execute(query, vars)
        return cursor

    def __getattr__(self, name):
        return getattr(self._conn, name)

DATABASE_NAME = "bimeh"

def get_db():
    conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
    try:
        yield conn
    finally:
        conn.close()

def get_month_dates(month_name: str) -> List[str]:
    if not month_name:
        return []

    clean_name = month_name.strip().upper()

    month_order = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
        "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
        "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }

    conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha ASC;")
    all_dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    if clean_name in ("TODOS", "ANUAL", "ALL", "TODOS LOS MESES"):
        return all_dates

    target_months: Set[int] = set()

    # Detección de nombres de mes en el texto (ej. "MARZO - SEPTIEMBRE", "MARZO 2026 - SEPTIEMBRE 2026", "DE MARZO A SEPTIEMBRE")
    words = re.findall(r"\b[A-Z]+\b", clean_name)
    found_months = [month_order[w] for w in words if w in month_order]
    if len(found_months) >= 2:
        ini, fin = min(found_months[0], found_months[-1]), max(found_months[0], found_months[-1])
        target_months = set(range(ini, fin + 1))
    elif len(found_months) == 1:
        target_months = {found_months[0]}

    # Rango numérico tipo "03-09" o "3-9"
    if not target_months:
        num_range_match = re.search(r"\b(\d{1,2})\s*-\s*(\d{1,2})\b", clean_name)
        if num_range_match:
            n1, n2 = int(num_range_match.group(1)), int(num_range_match.group(2))
            if 1 <= n1 <= 12 and 1 <= n2 <= 12:
                ini, fin = min(n1, n2), max(n1, n2)
                target_months = set(range(ini, fin + 1))

    # Mes numérico individual
    if not target_months and clean_name.isdigit():
        num_val = int(clean_name)
        if 1 <= num_val <= 12:
            target_months = {num_val}

    if not target_months:
        return all_dates

    filtered = []
    for d in all_dates:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            if dt.month in target_months:
                filtered.append(d)
        except ValueError:
            continue
    return filtered


def get_available_date_range(db=None) -> dict:
    """
    Retorna el rango dinámico de fechas y meses cargados en la tabla REPORTES de BIMEJ 12.
    """
    meses_nombres = {
        1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
        5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
        9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
    }
    close_conn = False
    if db is None:
        conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
        close_conn = True
    else:
        conn = db
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(to_date(fecha, 'YYYY-MM-DD')), MAX(to_date(fecha, 'YYYY-MM-DD')) FROM REPORTES;")
        row = cursor.fetchone()
        if row and row[0] and row[1]:
            min_d, max_d = row[0], row[1]
            min_nom = meses_nombres.get(min_d.month, "ENERO")
            max_nom = meses_nombres.get(max_d.month, "JULIO")
            return {
                "min_date": min_d.strftime("%Y-%m-%d"),
                "max_date": max_d.strftime("%Y-%m-%d"),
                "min_month": min_nom,
                "max_month": max_nom,
                "year": max_d.year,
                "texto": f"{min_nom} a {max_nom} de {max_d.year}"
            }
    except Exception:
        pass
    finally:
        if close_conn:
            try:
                conn.close()
            except Exception:
                pass
    return {
        "min_date": "2026-01-01",
        "max_date": "2026-07-31",
        "min_month": "ENERO",
        "max_month": "JULIO",
        "year": 2026,
        "texto": "ENERO a JULIO de 2026"
    }


def asegurar_optimizaciones_db():
    """
    Crea índices de rendimiento y vistas analíticas en PostgreSQL si aún no existen.
    Garantiza velocidad en JOINs y consultas sencillas para el Asistente de IA.
    """
    try:
        raw_conn = psycopg2.connect(**DB_CONN_PARAMS)
        cursor = raw_conn.cursor()

        # 1. Extensión pg_trgm e índice de trigramas para búsquedas LIKE
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_personal_nombre_trgm ON PERSONAL USING gin (UPPER(nombre) gin_trgm_ops);")
            raw_conn.commit()
        except Exception:
            raw_conn.rollback()

        # 2. Índices para Foreign Keys y estados
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_rp_id_personal ON REGISTRO_PERSONAL(id_personal);",
            "CREATE INDEX IF NOT EXISTS idx_rp_id_reporte ON REGISTRO_PERSONAL(id_reporte);",
            "CREATE INDEX IF NOT EXISTS idx_rp_id_sub_novedad ON REGISTRO_PERSONAL(id_sub_novedad);",
            "CREATE INDEX IF NOT EXISTS idx_personal_activos ON PERSONAL(id) WHERE fecha_retiro IS NULL OR fecha_retiro = '';",
            "CREATE INDEX IF NOT EXISTS idx_reportes_fecha ON REPORTES(fecha);",
            "CREATE INDEX IF NOT EXISTS idx_sub_novedades_nombre ON SUB_NOVEDADES(nombre);"
        ]
        for idx_sql in indices:
            try:
                cursor.execute(idx_sql)
                raw_conn.commit()
            except Exception:
                raw_conn.rollback()

        # 3. Vistas unificadas para el Asistente de IA
        vistas = [
            """
            CREATE OR REPLACE VIEW v_personal_resumen AS
            SELECT 
                p.id,
                p.cedula,
                p.nombre,
                CASE 
                    WHEN (p.fecha_retiro IS NULL OR p.fecha_retiro = '') THEN 'ACTIVO' 
                    ELSE 'RETIRADO' 
                END AS estado,
                p.fecha_retiro,
                COUNT(rp.id) AS total_novedades_historicas
            FROM PERSONAL p
            LEFT JOIN REGISTRO_PERSONAL rp ON rp.id_personal = p.id
            GROUP BY p.id, p.cedula, p.nombre, p.fecha_retiro;
            """,
            """
            CREATE OR REPLACE VIEW v_novedades_detalle AS
            SELECT 
                rp.id AS id_registro,
                p.cedula,
                p.nombre,
                CASE 
                    WHEN (p.fecha_retiro IS NULL OR p.fecha_retiro = '') THEN 'ACTIVO' 
                    ELSE 'RETIRADO' 
                END AS estado,
                r.fecha AS fecha_reporte,
                COALESCE(sn.nombre, 'SIN NOVEDAD') AS novedad,
                rp.descripcion,
                rp.fecha_inicio,
                rp.fecha_final
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON p.id = rp.id_personal
            JOIN REPORTES r ON r.id = rp.id_reporte
            LEFT JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad;
            """,
            """
            CREATE OR REPLACE VIEW v_conteo_novedades AS
            SELECT 
                COALESCE(sn.nombre, 'SIN NOVEDAD') AS novedad,
                COUNT(rp.id) AS total_dias_registrados,
                COUNT(DISTINCT rp.id_personal) AS total_personal_afectado
            FROM REGISTRO_PERSONAL rp
            JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
            GROUP BY sn.nombre;
            """
        ]
        for v_sql in vistas:
            try:
                cursor.execute(v_sql)
                raw_conn.commit()
            except Exception:
                raw_conn.rollback()

        # 4. Tablas para Memoria y Sesiones del Asistente de IA
        tablas_ia = [
            """
            CREATE TABLE IF NOT EXISTS IA_SESIONES (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL DEFAULT 'Nueva consulta',
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS IA_MENSAJES (
                id SERIAL PRIMARY KEY,
                id_sesion INT NOT NULL REFERENCES IA_SESIONES(id) ON DELETE CASCADE,
                rol VARCHAR(50) NOT NULL,
                contenido TEXT NOT NULL,
                metadatos JSONB DEFAULT '{}'::jsonb,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            "CREATE INDEX IF NOT EXISTS idx_ia_mensajes_sesion ON IA_MENSAJES(id_sesion);",
            "CREATE INDEX IF NOT EXISTS idx_ia_sesiones_actualizado ON IA_SESIONES(actualizado_en DESC);"
        ]
        for t_sql in tablas_ia:
            try:
                cursor.execute(t_sql)
                raw_conn.commit()
            except Exception:
                raw_conn.rollback()

        cursor.close()
        raw_conn.close()
        print("[DB-OPT] Indices, vistas y tablas de IA verificados correctamente en PostgreSQL.")
    except Exception as e:
        print(f"[DB-OPT] Aviso: no se pudieron aplicar optimizaciones automaticas de DB: {e}")

