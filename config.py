from auth import obtener_servicio_drive

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
drive = obtener_servicio_drive()

