import json
from config.auth import obtener_servicio_drive
from config.config import MONTHS, EXCEL_MIME
MONTH_FOLDERS = []
try:
    with open("config/carpeta_principal.json") as pf:
        MONTH_FOLDERS = json.load(pf)
except Exception:
    pass

def get_carpeta(ID):

    drive = obtener_servicio_drive()
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



def listar_dias_mes(target_month=None):
    meses = {}
    for mes in MONTH_FOLDERS:
        # Encontrar el nombre del mes
        mes_name = None
        for m in MONTHS:
            if m in mes["name"]:
                mes_name = m
                break
                
        if not mes_name:
            continue
            
        # Si hay un mes objetivo y no coincide, lo omitimos
        if target_month and mes_name != target_month:
            continue
            
        print(f"Listando archivos de Google Drive para el mes: {mes_name}...")
        archivos = get_carpeta(mes['id'])
        meses[mes_name] = archivos
        
    return meses

if __name__ == "__main__":
    with open("listado_meses.json","w") as ls:
        json.dump(listar_dias_mes(),ls,indent=4)


