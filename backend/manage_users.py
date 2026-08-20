"""
BIMEH - Gestor de Usuarios y Permisos
Uso:
  python manage_users.py list                 # Listar todos los usuarios
  python manage_users.py add                  # Crear un nuevo usuario interactivamente
  python manage_users.py seed                 # Crear usuarios administrativos iniciales
  python manage_users.py reset-password       # Cambiar contraseña de un usuario
  python manage_users.py toggle-active        # Activar/desactivar un usuario
"""

import sys
import os
import bcrypt

# Asegurar import de base de datos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import ConnectionWrapper, DB_CONN_PARAMS

def _get_db():
    try:
        conn = ConnectionWrapper(conn_params=DB_CONN_PARAMS)
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        sys.exit(1)

def listar_usuarios():
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id_usuario, u.nombre, u.correo, u.activo, u.ultimo_login, r.nombre AS rol
        FROM USUARIO u
        LEFT JOIN USUARIO_ROL ur ON u.id_usuario = ur.id_usuario
        LEFT JOIN ROL r ON ur.id_rol = r.id_rol
        ORDER BY u.id_usuario ASC;
    """)
    usuarios = cursor.fetchall()
    conn.close()

    print("\n==========================================================================================")
    print(f"{'ID':<4} | {'NOMBRE':<25} | {'CORREO':<30} | {'ROL':<15} | {'ACTIVO':<7} | {'ÚLTIMO LOGIN'}")
    print("==========================================================================================")
    if not usuarios:
        print("  No hay usuarios registrados en la base de datos.")
    for u in usuarios:
        activo_str = "SÍ" if u[3] else "NO"
        login_str = str(u[4])[:19] if u[4] else "Nunca"
        rol_str = u[5] or "Sin Rol"
        print(f"{u[0]:<4} | {u[1]:<25} | {u[2]:<30} | {rol_str:<15} | {activo_str:<7} | {login_str}")
    print("==========================================================================================\n")

def crear_usuario_interactivo():
    print("\n--- CREAR NUEVO USUARIO ---")
    nombre = input("Nombre completo: ").strip()
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

    rol_nombre = input("Rol (ADMINISTRATIVO / CONSULTA) [Default: ADMINISTRATIVO]: ").strip().upper() or "ADMINISTRATIVO"

    conn = _get_db()
    cursor = conn.cursor()
    try:
        # 1. Asegurar rol
        cursor.execute("SELECT id_rol FROM ROL WHERE nombre = %s;", (rol_nombre,))
        row_rol = cursor.fetchone()
        if not row_rol:
            cursor.execute("INSERT INTO ROL (nombre, descripcion) VALUES (%s, %s) RETURNING id_rol;", (rol_nombre, f"Rol {rol_nombre}"))
            id_rol = cursor.fetchone()[0]
        else:
            id_rol = row_rol[0]

        # 2. Hash de contraseña
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 3. Verificar si existe
        cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (correo,))
        existente = cursor.fetchone()
        if existente:
            id_usuario = existente[0]
            cursor.execute("""
                UPDATE USUARIO SET nombre = %s, password_hash = %s, activo = TRUE WHERE id_usuario = %s;
            """, (nombre, pw_hash, id_usuario))
            print(f"🔄 Usuario '{correo}' actualizado correctamente.")
        else:
            cursor.execute("""
                INSERT INTO USUARIO (nombre, correo, password_hash, activo)
                VALUES (%s, %s, %s, TRUE) RETURNING id_usuario;
            """, (nombre, correo, pw_hash))
            id_usuario = cursor.fetchone()[0]
            print(f"✨ Usuario '{correo}' creado con ID: {id_usuario}.")

        # 4. Asignar rol
        cursor.execute("""
            INSERT INTO USUARIO_ROL (id_usuario, id_rol) VALUES (%s, %s)
            ON CONFLICT (id_usuario, id_rol) DO NOTHING;
        """, (id_usuario, id_rol))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al crear usuario: {e}")
    finally:
        conn.close()

def reset_password():
    print("\n--- RESTABLECER CONTRASEÑA ---")
    correo = input("Correo del usuario: ").strip().lower()
    if not correo:
        print("❌ Correo requerido.")
        return

    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (correo,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ Usuario con correo '{correo}' no encontrado.")
        conn.close()
        return

    id_usuario = row[0]
    nueva_pw = input("Nueva contraseña: ").strip()
    if not nueva_pw:
        print("❌ La contraseña no puede estar vacía.")
        conn.close()
        return

    pw_hash = bcrypt.hashpw(nueva_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("UPDATE USUARIO SET password_hash = %s WHERE id_usuario = %s;", (pw_hash, id_usuario))
    conn.commit()
    conn.close()
    print(f"✅ Contraseña de '{correo}' actualizada con éxito.")

def toggle_active():
    print("\n--- ACTIVAR / DESACTIVAR USUARIO ---")
    correo = input("Correo del usuario: ").strip().lower()
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, activo FROM USUARIO WHERE correo = %s;", (correo,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ Usuario '{correo}' no encontrado.")
        conn.close()
        return

    id_usuario, activo = row
    nuevo_estado = not activo
    cursor.execute("UPDATE USUARIO SET activo = %s WHERE id_usuario = %s;", (nuevo_estado, id_usuario))
    conn.commit()
    conn.close()
    print(f"✅ Usuario '{correo}' ahora está {'ACTIVO' if nuevo_estado else 'INACTIVO'}.")

def seed_inicial():
    print("\n--- INICIALIZAR USUARIOS ADMINISTRATIVOS POR DEFECTO ---")
    conn = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ROL (nombre, descripcion) VALUES ('ADMINISTRATIVO', 'Acceso total al sistema') ON CONFLICT (nombre) DO NOTHING;")
        conn.commit()
        cursor.execute("SELECT id_rol FROM ROL WHERE nombre = 'ADMINISTRATIVO';")
        id_rol = cursor.fetchone()[0]

        default_admin = ("Administrador", "admin@bimeh.com", "AdminBimeh123!")
        cursor.execute("SELECT id_usuario FROM USUARIO WHERE correo = %s;", (default_admin[1],))
        if not cursor.fetchone():
            pw_hash = bcrypt.hashpw(default_admin[2].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO USUARIO (nombre, correo, password_hash, activo) VALUES (%s, %s, %s, TRUE) RETURNING id_usuario;",
                           (default_admin[0], default_admin[1], pw_hash))
            id_u = cursor.fetchone()[0]
            cursor.execute("INSERT INTO USUARIO_ROL (id_usuario, id_rol) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (id_u, id_rol))
            conn.commit()
            print(f"✅ Usuario admin por defecto creado: {default_admin[1]}")
        else:
            print(f"ℹ️  El usuario '{default_admin[1]}' ya existe.")
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("\n=============================================")
        print("      BIMEH - GESTIÓN DE USUARIOS           ")
        print("=============================================")
        print("1. Listar usuarios")
        print("2. Crear nuevo usuario")
        print("3. Cambiar contraseña")
        print("4. Activar / Desactivar usuario")
        print("5. Crear admin inicial por defecto")
        print("0. Salir")
        opcion = input("\nElige una opción (0-5): ").strip()
        if opcion == "1":
            listar_usuarios()
        elif opcion == "2":
            crear_usuario_interactivo()
        elif opcion == "3":
            reset_password()
        elif opcion == "4":
            toggle_active()
        elif opcion == "5":
            seed_inicial()
        else:
            print("Saliendo.")
        return

    cmd = sys.argv[1].lower()
    if cmd in ("list", "listar"):
        listar_usuarios()
    elif cmd in ("add", "crear"):
        crear_usuario_interactivo()
    elif cmd in ("reset-password", "passwd"):
        reset_password()
    elif cmd in ("toggle", "toggle-active"):
        toggle_active()
    elif cmd in ("seed", "init"):
        seed_inicial()
    else:
        print(f"❌ Comando no reconocido: '{cmd}'")
        print(__doc__)

if __name__ == "__main__":
    main()
