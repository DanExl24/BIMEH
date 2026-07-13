import psycopg2
import bcrypt
from datetime import datetime

def main():
    try:
        conn = psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_pPVueS4skO8j",
            host="ep-snowy-glade-aty6j16z-pooler.c-9.us-east-1.aws.neon.tech",
            sslmode="require"
        )
        cursor = conn.cursor()
        print("Conexión exitosa a PostgreSQL.")
    except Exception as e:
        print(f"Error al conectar con PostgreSQL: {e}")
        print("Por favor asegúrese de que PostgreSQL esté iniciado y de que los datos de acceso sean correctos.")
        return

    print("Creando tablas de autenticación si no existen...")
    
    # Create USUARIO table
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

    # Create ROL table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ROL (
        id_rol SERIAL PRIMARY KEY,
        nombre VARCHAR(255) UNIQUE NOT NULL,
        descripcion TEXT
    );
    """)

    # Create USUARIO_ROL table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USUARIO_ROL (
        id_usuario INTEGER REFERENCES USUARIO(id_usuario) ON DELETE CASCADE,
        id_rol INTEGER REFERENCES ROL(id_rol) ON DELETE CASCADE,
        PRIMARY KEY (id_usuario, id_rol)
    );
    """)
    conn.commit()
    print("Tablas creadas correctamente.")

    # Seed ROL
    print("Creando roles por defecto...")
    cursor.execute("INSERT INTO ROL (nombre, descripcion) VALUES ('ADMINISTRATIVO', 'Acceso de administración total al sistema') ON CONFLICT (nombre) DO NOTHING;")
    conn.commit()

    # Get id_rol for ADMINISTRATIVO
    cursor.execute("SELECT id_rol FROM ROL WHERE nombre = 'ADMINISTRATIVO';")
    id_rol = cursor.fetchone()[0]

    # Create default user
    email = "admin@bimeh.com"
    cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (email,))
    user_exists = cursor.fetchone()

    if not user_exists:
        print(f"Creando usuario por defecto: {email}")
        password = "AdminBimeh123!"
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        cursor.execute("""
        INSERT INTO USUARIO (nombre, correo, password_hash, activo)
        VALUES ('Administrador', %s, %s, TRUE) RETURNING id_usuario;
        """, (email, hashed_password))
        
        id_usuario = cursor.fetchone()[0]
        
        # Link user to role
        cursor.execute("""
        INSERT INTO USUARIO_ROL (id_usuario, id_rol)
        VALUES (%s, %s);
        """, (id_usuario, id_rol))
        
        conn.commit()
        print("Usuario administrativo creado con éxito.")
    else:
        print("El usuario administrativo ya existe. No se realizaron inserciones.")

    conn.close()
    print("Inicialización de seguridad de base de datos terminada.")

if __name__ == "__main__":
    main()
