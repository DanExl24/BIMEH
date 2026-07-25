import os
import json
import tempfile
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from app.database import ConnectionWrapper, NEON_CONN_PARAMS

# ---------------------------------------------------------------------------
# Rutas según entorno
# ---------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "credentials.json")
    TOKEN_PATH = os.path.join(os.getcwd(), "config", "token.json")
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

# ---------------------------------------------------------------------------
# credentials.json: en producción (Render) se escribe desde la env var
# GOOGLE_CREDENTIALS_JSON al arrancar, evitando subir el archivo a git.
# ---------------------------------------------------------------------------
def _asegurar_credentials():
    """Si credentials.json no existe pero hay env var, lo escribe en un temp."""
    if os.path.exists(CREDENTIALS_PATH):
        return CREDENTIALS_PATH

    env_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if env_json:
        tmp_path = os.path.join(tempfile.gettempdir(), "bimeh_credentials.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(env_json)
        print(f"[AUTH] credentials.json escrito desde env var en: {tmp_path}")
        return tmp_path

    raise FileNotFoundError(
        "No se encontró credentials.json ni la variable de entorno "
        "GOOGLE_CREDENTIALS_JSON. Configura la variable en el dashboard de Render."
    )

# ---------------------------------------------------------------------------
# Helper DB connection & auto-table creation
# ---------------------------------------------------------------------------
def _get_db_conn():
    try:
        conn = ConnectionWrapper(conn_params=NEON_CONN_PARAMS)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_oauth_tokens (
                correo_google VARCHAR(255) PRIMARY KEY,
                token_json TEXT NOT NULL,
                actualizado_en TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        return conn
    except Exception as e:
        print(f"[AUTH] No se pudo conectar/inicializar DB para tokens ({e}).")
        return None

def _leer_token_db(correo_google: str | None = None) -> str | None:
    """Lee el token JSON de un usuario especifico o el mas reciente de la BD."""
    conn = _get_db_conn()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        if correo_google:
            cursor.execute(
                "SELECT token_json FROM google_oauth_tokens WHERE correo_google = %s",
                (correo_google,)
            )
        else:
            cursor.execute(
                "SELECT token_json FROM google_oauth_tokens ORDER BY actualizado_en DESC LIMIT 1"
            )
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"[AUTH] Error leyendo token de BD ({e}).")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass

def _guardar_token_db(correo_google: str, token_json: str):
    """Guarda o actualiza el token JSON de un usuario en la BD."""
    conn = _get_db_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO google_oauth_tokens (correo_google, token_json, actualizado_en)
            VALUES (%s, %s, NOW())
            ON CONFLICT (correo_google)
            DO UPDATE SET token_json = EXCLUDED.token_json, actualizado_en = NOW();
        """, (correo_google, token_json))
        conn.commit()
        print(f"[AUTH] Token de '{correo_google}' guardado correctamente en la BD.")
    except Exception as e:
        print(f"[AUTH] Error guardando token en BD ({e}).")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def _eliminar_token_db(correo_google: str):
    """Elimina el token de un usuario de la BD."""
    conn = _get_db_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM google_oauth_tokens WHERE correo_google = %s",
            (correo_google,)
        )
        conn.commit()
        print(f"[AUTH] Token de '{correo_google}' eliminado de la BD.")
    except Exception as e:
        print(f"[AUTH] Error eliminando token de BD ({e}).")
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def eliminar_token_existente(correo_google: str | None = None):
    """Elimina el token de un usuario (BD) o el archivo local si no hay correo."""
    if correo_google:
        _eliminar_token_db(correo_google)
    if os.path.exists(TOKEN_PATH):
        try:
            os.remove(TOKEN_PATH)
            print(f"[AUTH] Token local eliminado: {TOKEN_PATH}")
        except Exception as e:
            print(f"[AUTH] Error eliminando token local: {e}")

def generar_oauth_url(redirect_uri: str) -> str:
    """Genera la URL de autorización de Google OAuth."""
    creds_path = _asegurar_credentials()
    flow = Flow.from_client_secrets_file(creds_path, scopes=SCOPES, redirect_uri=redirect_uri)
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url

def intercambiar_codigo_oauth(code: str, redirect_uri: str):
    """
    Intercambia el código OAuth por credenciales y las guarda en BD y local.
    Returns creds.
    """
    creds_path = _asegurar_credentials()
    flow = Flow.from_client_secrets_file(creds_path, scopes=SCOPES, redirect_uri=redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials

    correo_google = "desconocido"
    try:
        import google.oauth2.id_token
        import google.auth.transport.requests
        request = google.auth.transport.requests.Request()
        id_info = google.oauth2.id_token.verify_oauth2_token(creds.id_token, request)
        correo_google = id_info.get("email", "desconocido")
    except Exception as e:
        print(f"[AUTH] No se pudo extraer email de id_token ({e}).")

    token_json = creds.to_json()

    # Guardar en BD (produccion) y en archivo local (desarrollo)
    _guardar_token_db(correo_google, token_json)
    try:
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(token_json)
    except Exception as e:
        print(f"[AUTH] Error al escribir token local: {e}")

    return creds

def obtener_credenciales(correo_google: str | None = None, force_new: bool = False) -> Credentials:
    """
    Obtiene credenciales válidas para un usuario (o el token mas reciente).
    Busca en BD primero, luego en archivo local. Refresca si expiro.
    """
    creds = None

    if force_new:
        eliminar_token_existente(correo_google)

    # 1. Intentar cargar desde BD
    token_json = _leer_token_db(correo_google)
    if token_json:
        try:
            creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
        except Exception as e:
            print(f"[AUTH] Error cargando token de BD: {e}")
            creds = None

    # 2. Fallback: archivo local (desarrollo)
    if not creds and os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"[AUTH] Error cargando token local: {e}")
            creds = None

    # 3. Refrescar si esta expirado
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                if correo_google:
                    _guardar_token_db(correo_google, creds.to_json())
                try:
                    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                        f.write(creds.to_json())
                except Exception:
                    pass
            except Exception as e:
                print(f"[AUTH] No se pudo refrescar el token ({e}).")
                creds = None
        else:
            creds = None

    # 4. Si se ejecuto en Render sin token valido
    if not creds:
        raise Exception(
            "No hay token de Google Drive autorizado en el servidor. "
            "Inicie sesión con Google en la sección Sincronizar."
        )

    return creds

def obtener_servicio_drive(correo_google: str | None = None, force_new: bool = False):
    return build("drive", "v3", credentials=obtener_credenciales(correo_google, force_new))

def obtener_servicio_sheets(correo_google: str | None = None, force_new: bool = False):
    return build("sheets", "v4", credentials=obtener_credenciales(correo_google, force_new))