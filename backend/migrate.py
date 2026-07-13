import sqlite3
import psycopg2
from psycopg2.extras import execute_values

def migrate():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect("bimej12.db")
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_pPVueS4skO8j",
            host="ep-snowy-glade-aty6j16z-pooler.c-9.us-east-1.aws.neon.tech",
            sslmode="require"
        )
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("Please make sure PostgreSQL is running, the database 'BIMEH' exists, and the password is 'postgres'.")
        return
        
    print("Connected to databases. Dropping existing tables in PostgreSQL...")
    pg_cursor.execute("DROP TABLE IF EXISTS REGISTRO_PERSONAL;")
    pg_cursor.execute("DROP TABLE IF EXISTS REPORTES;")
    pg_cursor.execute("DROP TABLE IF EXISTS SUB_NOVEDADES;")
    pg_cursor.execute("DROP TABLE IF EXISTS PERSONAL;")
    
    print("Creating tables in PostgreSQL...")
    pg_cursor.execute("""
    CREATE TABLE PERSONAL (
        id SERIAL PRIMARY KEY,
        cedula BIGINT UNIQUE,
        nombre VARCHAR(255),
        fecha_retiro VARCHAR(50)
    );
    """)
    
    pg_cursor.execute("""
    CREATE TABLE SUB_NOVEDADES (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE
    );
    """)
    
    pg_cursor.execute("""
    CREATE TABLE REPORTES (
        id SERIAL PRIMARY KEY,
        fecha VARCHAR(50) UNIQUE,
        archivo VARCHAR(255)
    );
    """)
    
    pg_cursor.execute("""
    CREATE TABLE REGISTRO_PERSONAL (
        id SERIAL PRIMARY KEY,
        id_reporte INTEGER REFERENCES REPORTES(id),
        id_personal INTEGER REFERENCES PERSONAL(id),
        id_sub_novedad INTEGER REFERENCES SUB_NOVEDADES(id),
        descripcion TEXT,
        fecha_inicio VARCHAR(50),
        fecha_final VARCHAR(50)
    );
    """)
    pg_conn.commit()
    
    # Migrate PERSONAL
    print("Migrating PERSONAL...")
    sqlite_cursor.execute("SELECT id, cedula, nombre, fecha_retiro FROM PERSONAL;")
    rows = sqlite_cursor.fetchall()
    if rows:
        execute_values(
            pg_cursor,
            "INSERT INTO PERSONAL (id, cedula, nombre, fecha_retiro) VALUES %s",
            rows
        )
        
    # Migrate SUB_NOVEDADES
    print("Migrating SUB_NOVEDADES...")
    sqlite_cursor.execute("SELECT id, nombre FROM SUB_NOVEDADES;")
    rows = sqlite_cursor.fetchall()
    if rows:
        execute_values(
            pg_cursor,
            "INSERT INTO SUB_NOVEDADES (id, nombre) VALUES %s",
            rows
        )
        
    # Migrate REPORTES
    print("Migrating REPORTES...")
    sqlite_cursor.execute("SELECT id, fecha, archivo FROM REPORTES;")
    rows = sqlite_cursor.fetchall()
    if rows:
        execute_values(
            pg_cursor,
            "INSERT INTO REPORTES (id, fecha, archivo) VALUES %s",
            rows
        )
        
    # Migrate REGISTRO_PERSONAL
    print("Migrating REGISTRO_PERSONAL...")
    sqlite_cursor.execute("SELECT id, id_reporte, id_personal, id_sub_novedad, descripcion, fecha_inicio, fecha_final FROM REGISTRO_PERSONAL;")
    rows = sqlite_cursor.fetchall()
    if rows:
        execute_values(
            pg_cursor,
            "INSERT INTO REGISTRO_PERSONAL (id, id_reporte, id_personal, id_sub_novedad, descripcion, fecha_inicio, fecha_final) VALUES %s",
            rows
        )
        
    print("Resetting auto-increment sequences...")
    pg_cursor.execute("SELECT setval(pg_get_serial_sequence('PERSONAL', 'id'), coalesce(max(id), 1)) FROM PERSONAL;")
    pg_cursor.execute("SELECT setval(pg_get_serial_sequence('SUB_NOVEDADES', 'id'), coalesce(max(id), 1)) FROM SUB_NOVEDADES;")
    pg_cursor.execute("SELECT setval(pg_get_serial_sequence('REPORTES', 'id'), coalesce(max(id), 1)) FROM REPORTES;")
    pg_cursor.execute("SELECT setval(pg_get_serial_sequence('REGISTRO_PERSONAL', 'id'), coalesce(max(id), 1)) FROM REGISTRO_PERSONAL;")
    
    pg_conn.commit()
    
    sqlite_conn.close()
    pg_conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
