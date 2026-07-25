import bcrypt
from app.database import ConnectionWrapper, NEON_CONN_PARAMS

def crear_usuario():
    print("\n=============================================")
    print("      BIMEH - CREAR NUEVO USUARIO EN BD     ")
    print("=============================================\n")

    nombre = input("Nombre completo del usuario: ").strip()
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return

    correo = input("Correo electrónico: ").strip().lower()
    if not correo:
        print("❌ El correo no puede estar vacío.")
        return

    password = input("Contraseña: ").strip()
    if not password:
        print("❌ La contraseña no puede estar vacía.")
        return

    try:
        conn = ConnectionWrapper(conn_params=NEON_CONN_PARAMS)
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (correo,))
        existente = cursor.fetchone()

        # Obtener ID del rol ADMINISTRATIVO
        cursor.execute("SELECT id_rol FROM ROL WHERE nombre = 'ADMINISTRATIVO';")
        row_rol = cursor.fetchone()
        if not row_rol:
            cursor.execute("INSERT INTO ROL (nombre, descripcion) VALUES ('ADMINISTRATIVO', 'Acceso total') RETURNING id_rol;")
            id_rol = cursor.fetchone()[0]
        else:
            id_rol = row_rol[0]

        # Hashear la contraseña con bcrypt
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if existente:
            id_usuario = existente[0]
            cursor.execute("""
                UPDATE USUARIO 
                SET nombre = %s, password_hash = %s, activo = TRUE 
                WHERE id_usuario = %s;
            """, (nombre, pw_hash, id_usuario))
            print(f"\n✅ Usuario '{correo}' actualizado con éxito.")
        else:
            cursor.execute("""
                INSERT INTO USUARIO (nombre, correo, password_hash, activo)
                VALUES (%s, %s, %s, TRUE) RETURNING id_usuario;
            """, (nombre, correo, pw_hash))
            id_usuario = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO USUARIO_ROL (id_usuario, id_rol) 
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
            """, (id_usuario, id_rol))
            print(f"\n✅ Usuario '{correo}' creado con éxito (ID: {id_usuario}).")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"\n❌ Error al crear el usuario en la BD: {e}")

if __name__ == "__main__":
    crear_usuario()
