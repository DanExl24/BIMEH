from config.auth import obtener_servicio_drive
import json
drive = obtener_servicio_drive()

months = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]

filtros = " or ".join(f"name contains '{m}'" for m in months)

def p_folder():
    resultado = (
    drive.files()
    .list(
        q=f"'17X6rJsSgY6N4aO9LbNTCKk0vLxHpnYWL' in parents and mimeType = 'application/vnd.google-apps.folder' and ({filtros})",
        orderBy = "name",
        fields="files(id,name,mimeType,webViewLink)"
    )
    .execute()
    ).get("files",[])
    return resultado
PRINCIPAL_FOLDER = p_folder()



with open("config/carpeta_principal.json","w") as resultado:
    json.dump(PRINCIPAL_FOLDER,resultado,indent=4)