import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import sys

# Determinar rutas dinámicamente según si corre compilado (producción) o en código fuente (desarrollo)
if getattr(sys, 'frozen', False):
    # En producción, credentials.json viene empaquetado en el directorio temporal sys._MEIPASS
    BASE_DIR = sys._MEIPASS
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "credentials.json")
    
    # token.json (que se genera y refresca dinámicamente) se almacena en el directorio actual de ejecución
    # del subproceso (el cual Electron establecerá en la carpeta AppData escribible del usuario)
    TOKEN_PATH = os.path.join(os.getcwd(), "config", "token.json")
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
else:
    # En desarrollo local
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
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(f"No se encontró credentials.json en: {CREDENTIALS_PATH}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"No se encontró credentials.json en: {CREDENTIALS_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Guardar el token para que persista en el dispositivo del usuario
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