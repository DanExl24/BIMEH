import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List

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
    month_order = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
        "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
        "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }
    month_num = month_order.get(month_name.upper(), 1)
    
    conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha ASC;")
    all_dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    filtered = []
    for d in all_dates:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            if dt.month == month_num:
                filtered.append(d)
        except ValueError:
            continue
    return filtered


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

        cursor.close()
        raw_conn.close()
        print("[DB-OPT] Indices y vistas optimizadas verificados correctamente en PostgreSQL.")
    except Exception as e:
        print(f"[DB-OPT] Aviso: no se pudieron aplicar optimizaciones automaticas de DB: {e}")

