import sys
import os
import bcrypt

# Asegurar importación de app.database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import ConnectionWrapper, DB_CONN_PARAMS

# ==============================================================================
# CONFIGURACIÓN DE USUARIOS INICIALES (EDITA AQUÍ TUS CREDENCIALES)
# ==============================================================================
USUARIOS_INICIALES = [
    {
        "nombre": "alejo",
        "correo": "alejopmotta@gmail.com",
        "password": "alejo123",
        "rol": "ADMINISTRATIVO"
    },
    {
        "nombre": "jorge",
        "correo": "jorge@bimeh.com",
        "password": "jorge123",
        "rol": "ADMINISTRATIVO"
    }
]
# ==============================================================================

def crear_usuarios_iniciales():
    print("\n====================================================")
    print("      BIMEH - REGISTRO DE USUARIOS INICIALES        ")
    print("====================================================\n")

    try:
        conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
        cursor = conn.cursor()
        print(f"✅ Conectado a la base de datos: {DB_CONN_PARAMS.get('dbname')}\n")
    except Exception as e:
        print(f"❌ Error al conectar con PostgreSQL: {e}")
        print("Asegúrate de que PostgreSQL esté corriendo y la base de datos exista.")
        return

    for u in USUARIOS_INICIALES:
        nombre = u["nombre"].strip()
        correo = u["correo"].strip().lower()
        password = u["password"].strip()
        nombre_rol = u["rol"].strip().upper()

        if not correo or not password:
            print(f"⚠️ Saltando usuario con correo/contraseña vacíos.")
            continue

        try:
            # 1. Obtener o crear el rol
            cursor.execute("SELECT id_rol FROM ROL WHERE nombre = %s;", (nombre_rol,))
            row_rol = cursor.fetchone()
            if not row_rol:
                cursor.execute(
                    "INSERT INTO ROL (nombre, descripcion) VALUES (%s, %s) RETURNING id_rol;",
                    (nombre_rol, f"Rol {nombre_rol}")
                )
                id_rol = cursor.fetchone()[0]
            else:
                id_rol = row_rol[0]

            # 2. Hashear contraseña con bcrypt
            pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 3. Verificar si el usuario existe
            cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (correo,))
            existente = cursor.fetchone()

            if existente:
                id_usuario = existente[0]
                cursor.execute("""
                    UPDATE USUARIO 
                    SET nombre = %s, password_hash = %s, activo = TRUE 
                    WHERE id_usuario = %s;
                """, (nombre, pw_hash, id_usuario))
                print(f"🔄 Usuario '{correo}' actualizado correctamente.")
            else:
                cursor.execute("""
                    INSERT INTO USUARIO (nombre, correo, password_hash, activo)
                    VALUES (%s, %s, %s, TRUE) RETURNING id_usuario;
                """, (nombre, correo, pw_hash))
                id_usuario = cursor.fetchone()[0]
                print(f"✨ Usuario '{correo}' creado correctamente (ID: {id_usuario}).")

            # 4. Asignar rol al usuario
            cursor.execute("""
                INSERT INTO USUARIO_ROL (id_usuario, id_rol) 
                VALUES (%s, %s) 
                ON CONFLICT DO NOTHING;
            """, (id_usuario, id_rol))

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"❌ Error al procesar al usuario '{correo}': {e}")

    conn.close()
    print("\n🎉 Proceso de creación de usuarios finalizado con éxito.")

if __name__ == "__main__":
    crear_usuarios_iniciales()
