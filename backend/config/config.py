import os
from .auth import obtener_servicio_drive

MONTHS = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE"
]

FOLDER_MIME = "application/vnd.google-apps.folder"
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# ID de la carpeta principal del año en Google Drive
PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", "17X6rJsSgY6N4aO9LbNTCKk0vLxHpnYWL")

# Tiempo en segundos que permanecen visibles los logs y resultados de sincronización en la interfaz
SYNC_STATUS_AUTO_DISMISS_SECONDS = 20

def get_drive_service():
    return obtener_servicio_drive()
