import os
import json
from config.auth import obtener_servicio_drive
from config.config import MONTHS, EXCEL_MIME, FOLDER_MIME

PARENT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", "17X6rJsSgY6N4aO9LbNTCKk0vLxHpnYWL")

def obtener_carpetas_meses(drive=None):
    """
    Obtiene las carpetas correspondientes a cada mes en Google Drive dinámicamente.
    1. Consulta en vivo a Google Drive bajo PARENT_FOLDER_ID o por nombre de mes.
    2. Actualiza el archivo de caché local 'config/carpeta_principal.json'.
    3. Si no hay conexión, usa el caché local existente como respaldo.
    """
    if drive is None:
        try:
            drive = obtener_servicio_drive()
        except Exception as e:
            print(f"⚠️ No se pudo obtener el servicio de Drive: {e}")
            drive = None

    month_folders = []

    if drive:
        try:
            print(f"🔍 Consultando carpetas de meses en Google Drive (Carpeta Principal: {PARENT_FOLDER_ID})...")
            # Consulta dentro de la carpeta principal
            filtros = " or ".join(f"name contains '{m}'" for m in MONTHS)
            q = f"'{PARENT_FOLDER_ID}' in parents and mimeType = '{FOLDER_MIME}' and trashed = false and ({filtros})"
            
            response = drive.files().list(
                q=q,
                orderBy="name",
                fields="files(id, name, mimeType, webViewLink)",
                pageSize=100
            ).execute()
            
            found_folders = response.get("files", [])
            
            # Si no se encontraron por carpeta padre (por ejemplo si los IDs de carpeta cambiaron),
            # buscar a nivel global en todo el Drive por nombre de mes
            if not found_folders:
                print("ℹ️ No se encontraron subcarpetas bajo el ID principal. Buscando carpetas de meses en todo Google Drive...")
                q_global = f"mimeType = '{FOLDER_MIME}' and trashed = false and ({filtros})"
                response = drive.files().list(
                    q=q_global,
                    orderBy="name",
                    fields="files(id, name, mimeType, webViewLink)",
                    pageSize=100
                ).execute()
                found_folders = response.get("files", [])

            if found_folders:
                month_folders = found_folders
                print(f"✅ Se encontraron {len(month_folders)} carpetas de meses en Google Drive:")
                for f in month_folders:
                    print(f"   📂 {f['name']} (ID: {f['id']})")
                
                # Actualizar caché local
                try:
                    os.makedirs("config", exist_ok=True)
                    with open("config/carpeta_principal.json", "w", encoding="utf-8") as pf:
                        json.dump(month_folders, pf, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(f"⚠️ No se pudo guardar config/carpeta_principal.json: {e}")
        except Exception as e:
            print(f"⚠️ Error consultando carpetas de Drive en vivo: {e}. Usando caché local.")

    # Fallback al archivo local si la consulta en vivo falló o no devolvió resultados
    if not month_folders:
        try:
            with open("config/carpeta_principal.json", "r", encoding="utf-8") as pf:
                month_folders = json.load(pf)
                print(f"📁 Cargadas {len(month_folders)} carpetas desde el archivo local config/carpeta_principal.json")
        except Exception:
            month_folders = []

    return month_folders


def get_carpeta(ID, drive=None):
    """
    Lista todos los archivos de Excel dentro de una carpeta específica de Google Drive.
    """
    if drive is None:
        drive = obtener_servicio_drive()

    try:
        resultado = (
            drive.files()
            .list(
                q=f"'{ID}' in parents and trashed = false and (mimeType = '{EXCEL_MIME}' or name contains '.xlsx' or name contains '.xls')",
                fields="files(id, name, mimeType, webViewLink)",
                pageSize=100
            )
            .execute()
        ).get("files", [])

        # Filtrar archivos temporales de Office (~$archivo.xlsx)
        archivos_validos = [
            archivo
            for archivo in resultado
            if not archivo["name"].startswith("~$")
        ]
        return archivos_validos
    except Exception as e:
        print(f"❌ Error obteniendo archivos de la carpeta {ID}: {e}")
        return []


def listar_dias_mes(target_month=None, drive=None):
    """
    Descubre las carpetas de meses en Drive y lista los archivos Excel para el mes solicitado o todos.
    """
    if drive is None:
        try:
            drive = obtener_servicio_drive()
        except Exception as e:
            print(f"❌ Error conectando con Drive en listar_dias_mes: {e}")

    month_folders = obtener_carpetas_meses(drive=drive)
    meses = {}

    target_month_upper = target_month.upper() if target_month else None

    for mes in month_folders:
        nombre_carpeta = mes.get("name", "").upper()

        # Identificar a qué mes corresponde el nombre de la carpeta
        mes_name = None
        for m in MONTHS:
            if m in nombre_carpeta:
                mes_name = m
                break

        if not mes_name:
            continue

        # Si el usuario pidió sincronizar un mes específico y este no coincide, ignorar
        if target_month_upper and mes_name != target_month_upper:
            continue

        print(f"📄 Listando archivos de Google Drive para: {mes_name} (Carpeta: '{mes['name']}', ID: {mes['id']})...")
        archivos = get_carpeta(mes['id'], drive=drive)
        print(f"   -> {len(archivos)} archivos encontrados en {mes_name}.")
        meses[mes_name] = archivos

    return meses


if __name__ == "__main__":
    resultado = listar_dias_mes()
    with open("listado_meses.json", "w", encoding="utf-8") as ls:
        json.dump(resultado, ls, indent=4, ensure_ascii=False)
    print("Listado de meses actualizado con éxito en listado_meses.json.")
