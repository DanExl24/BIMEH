import json
from config.auth import obtener_servicio_drive
from config.config import MONTHS, EXCEL_MIME
drive = obtener_servicio_drive()

MONTH_FOLDERS = {}

with open("config/carpeta_principal.json") as pf:
    MONTH_FOLDERS = json.load(pf)


def get_carpeta(ID):
    resultado = (
    drive.files()
    .list(
        q=f"'{ID}' in parents and mimeType = '{EXCEL_MIME}' and trashed = false",
        fields="files(id,name,mimeType,webViewLink)"
    )
    .execute()
    ).get("files",[])
    return [
        archivo
        for archivo in resultado
        if not archivo["name"].startswith("~$")
    ]


def listar_dias_mes():
    meses = {}
    for mes in MONTH_FOLDERS:
        archivos = get_carpeta(mes['id'])
        for m in MONTHS:
            if m in mes["name"]:
                meses[m] = archivos
                break
    return meses

if __name__ == "__main__":
    with open("listado_meses.json","w") as ls:
        json.dump(listar_dias_mes(),ls,indent=4)


