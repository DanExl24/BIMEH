import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List

NEON_CONN_PARAMS = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_pPVueS4skO8j",
    "host": "ep-snowy-glade-aty6j16z-pooler.c-9.us-east-1.aws.neon.tech",
    "sslmode": "require"
}

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
        self._conn_params = conn_params or NEON_CONN_PARAMS
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
    conn = ConnectionWrapper(conn_params=NEON_CONN_PARAMS)
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
    
    conn = ConnectionWrapper(conn_params=NEON_CONN_PARAMS)
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
