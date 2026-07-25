import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build

import sys

# Determinar rutas dinámicamente según si corre compilado (producción) o en código fuente (desarrollo)
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

def eliminar_token_existente():
    """Elimina el archivo token.json si existe en TOKEN_PATH."""
    if os.path.exists(TOKEN_PATH):
        try:
            os.remove(TOKEN_PATH)
            print(f"Token previo eliminado: {TOKEN_PATH}")
        except Exception as e:
            print(f"Error eliminando token previo ({TOKEN_PATH}): {e}")

def generar_oauth_url(redirect_uri: str) -> str:
    """Genera la URL de autorización oficial de Google OAuth para la web/móvil."""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"No se encontró credentials.json en: {CREDENTIALS_PATH}")
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url

def intercambiar_codigo_oauth(code: str, redirect_uri: str):
    """Intercambia el código retornado por Google y guarda token.json."""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"No se encontró credentials.json en: {CREDENTIALS_PATH}")
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as token:
        token.write(creds.to_json())
    return creds

def obtener_credenciales(force_new: bool = False):
    creds = None

    if force_new:
        eliminar_token_existente()

    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(
                TOKEN_PATH,
                SCOPES
            )
        except Exception as e:
            print(f"Error cargando token existente: {e}. Se solicitará nueva autenticación.")
            eliminar_token_existente()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"No se pudo refrescar el token ({e}). Iniciando flujo OAuth desde cero...")
                eliminar_token_existente()
                creds = None

        if not creds:
            if os.environ.get("RENDER"):
                raise Exception("No hay token de Google Drive autorizado en el servidor. Inicie sesión con Google en la sección Sincronizar.")
            
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"No se encontró credentials.json en: {CREDENTIALS_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

    return creds

def obtener_servicio_drive(force_new: bool = False):
    return build(
        "drive",
        "v3",
        credentials=obtener_credenciales(force_new=force_new)
    )

def obtener_servicio_sheets(force_new: bool = False):
    return build(
        "sheets",
        "v4",
        credentials=obtener_credenciales(force_new=force_new)
    )
