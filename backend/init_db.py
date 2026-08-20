import sys
import os
import psycopg2
import bcrypt

# Asegurar import de app.database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import ConnectionWrapper, DB_CONN_PARAMS

def inicializar_base_de_datos():
    print("====================================================")
    print("   BIMEH - INICIALIZACIÓN DE BASE DE DATOS LOCAL   ")
    print("====================================================\n")
    
    print(f"📌 Conectando a PostgreSQL local:")
    print(f"   • Host: {DB_CONN_PARAMS.get('host')}")
    print(f"   • Puerto: {DB_CONN_PARAMS.get('port')}")
    print(f"   • Usuario: {DB_CONN_PARAMS.get('user')}")
    print(f"   • Base de Datos: {DB_CONN_PARAMS.get('dbname')}\n")

    try:
        conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
        cursor = conn.cursor()
        print("✅ Conexión establecida con éxito.\n")
    except Exception as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        print("\n💡 Verifica lo siguiente:")
        print("   1. PostgreSQL está instalado y corriendo en tu equipo.")
        print("   2. pgAdmin (o psql) se conectó y creaste la base de datos 'bimeh'.")
        print("   3. Si tu contraseña de postgres no es 'postgres', crea/edita el archivo .env en la carpeta backend con:")
        print("      DB_PASSWORD=tu_contraseña_aqui\n")
        return False

    try:
        print("🛠️  Creando estructura de tablas limpias...")

        # 1. PERSONAL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PERSONAL (
            id SERIAL PRIMARY KEY,
            cedula BIGINT UNIQUE,
            nombre VARCHAR(255),
            fecha_retiro VARCHAR(50)
        );
        """)

        # 2. SUB_NOVEDADES
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SUB_NOVEDADES (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) UNIQUE
        );
        """)

        # 3. REPORTES
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS REPORTES (
            id SERIAL PRIMARY KEY,
            fecha VARCHAR(50) UNIQUE,
            archivo VARCHAR(255)
        );
        """)

        # 4. REGISTRO_PERSONAL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS REGISTRO_PERSONAL (
            id SERIAL PRIMARY KEY,
            id_reporte INTEGER REFERENCES REPORTES(id) ON DELETE CASCADE,
            id_personal INTEGER REFERENCES PERSONAL(id) ON DELETE CASCADE,
            id_sub_novedad INTEGER REFERENCES SUB_NOVEDADES(id) ON DELETE SET NULL,
            descripcion TEXT,
            fecha_inicio VARCHAR(50),
            fecha_final VARCHAR(50)
        );
        """)

        # 5. USUARIO
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USUARIO (
            id_usuario SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            correo VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_login TIMESTAMP
        );
        """)

        # 6. ROL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ROL (
            id_rol SERIAL PRIMARY KEY,
            nombre VARCHAR(255) UNIQUE NOT NULL,
            descripcion TEXT
        );
        """)

        # 7. USUARIO_ROL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USUARIO_ROL (
            id_usuario INTEGER REFERENCES USUARIO(id_usuario) ON DELETE CASCADE,
            id_rol INTEGER REFERENCES ROL(id_rol) ON DELETE CASCADE,
            PRIMARY KEY (id_usuario, id_rol)
        );
        """)

        # 8. GOOGLE OAUTH TOKENS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS google_oauth_tokens (
            correo_google VARCHAR(255) PRIMARY KEY,
            token_json TEXT NOT NULL,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        print("✅ Tablas creadas/verificadas correctamente.")

        # Insertar Rol ADMINISTRATIVO
        cursor.execute("""
            INSERT INTO ROL (nombre, descripcion)
            VALUES ('ADMINISTRATIVO', 'Acceso de administración total al sistema')
            ON CONFLICT (nombre) DO NOTHING;
        """)
        conn.commit()

        cursor.execute("SELECT id_rol FROM ROL WHERE nombre = 'ADMINISTRATIVO';")
        id_rol = cursor.fetchone()[0]

        # Crear Usuario Administrador por defecto si no existe
        email_admin = "admin@bimeh.com"
        cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (email_admin,))
        admin_exists = cursor.fetchone()

        if not admin_exists:
            password = "AdminBimeh123!"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute("""
                INSERT INTO USUARIO (nombre, correo, password_hash, activo)
                VALUES ('Administrador', %s, %s, TRUE)
                RETURNING id_usuario;
            """, (email_admin, hashed))
            id_user = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO USUARIO_ROL (id_usuario, id_rol)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (id_user, id_rol))
            conn.commit()
            print(f"✅ Usuario admin por defecto creado con éxito:")
            print(f"   • Correo: {email_admin}")
            print(f"   • Contraseña: {password}")
        else:
            print(f"ℹ️  El usuario admin '{email_admin}' ya existe.")

        conn.close()
        print("\n🎉 Base de datos 'bimeh' inicializada limpia y lista para su uso.")
        return True

    except Exception as e:
        print(f"\n❌ Ocurrió un error al crear la estructura de tablas: {e}")
        return False

if __name__ == "__main__":
    inicializar_base_de_datos()
