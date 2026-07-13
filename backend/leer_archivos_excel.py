from openpyxl import load_workbook
import json
from googleapiclient.http import MediaIoBaseDownload
import io
from config.config import drive
import openpyxl
import re
from dateparser import parse
from pathlib import Path


def hoja_de_trabajo(file):
    # Hacer la peticion aq google drive al archivo de programas regulares por medio de la ID del archivo
    request = drive.files().get_media(fileId=file['id'])

    # crear un archivo en memoria RAM
    excel = io.BytesIO()

    # Descargar el archivo de drive y escribir sus datos dentro de la variable excel, asi se genera el archivo en memoria
    downloader = MediaIoBaseDownload(excel, request)

    # Variable para saber cuando termina la descarga
    done = False
    # Descargar el archivo
    while not done:
        _, done = downloader.next_chunk() #Descargar por pedazos (chuncks)

    excel.seek(0) #Leer desde el comienzo del cursor

    wb = load_workbook(excel, read_only=True, data_only=True)
    hoja = wb["DEMOSTRATIVO"]
    return hoja

import datetime
import calendar

MESES_MAP = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
    "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
    "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

def parse_date_from_filename(name):
    # Intentar extraer día, mes y año usando regex
    # Ejemplo: "BIMEJ PARTE DEMOSTRATIVO 11 JULIO 2026.xlsx"
    pattern = r"(\d{1,2})\s+(?:de\s+)?(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)\s+(\d{4})"
    match = re.search(pattern, name, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).upper()
        year = int(match.group(3))
        month = MESES_MAP.get(month_str, 1)
        try:
            return datetime.date(year, month, day).isoformat()
        except ValueError:
            pass
            
    # Intentar extraer sin año (asumiendo 2026)
    # Ejemplo: "BIMEJ PARTE DEMOSTRATIVO 11 JULIO.xlsx"
    pattern_no_year = r"(\d{1,2})\s+(?:de\s+)?(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)"
    match_ny = re.search(pattern_no_year, name, re.IGNORECASE)
    if match_ny:
        day = int(match_ny.group(1))
        month_str = match_ny.group(2).upper()
        month = MESES_MAP.get(month_str, 1)
        try:
            return datetime.date(2026, month, day).isoformat()
        except ValueError:
            pass
            
    return None

def obtener_hojas(db=None):
    # Cargar el listado de archivos agrupados por mes
    with open("listado_meses.json", encoding="utf-8") as l:
        listado_meses = json.load(l)

    errors = []
    
    # Obtener fechas en base de datos si db está disponible
    dates_in_db = set()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT fecha FROM REPORTES;")
            dates_in_db = {row[0] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error consultando fechas en base de datos: {e}")
            dates_in_db = set()

    # Recorrer cada mes (ENERO, FEBRERO, ...)
    for mes, archivos in listado_meses.items():
        if mes not in MESES_MAP:
            continue
            
        archivoF = Path(f"listadoMeses/{mes}.json")
        
        datos_archivo = {}
        if archivoF.exists():
            try:
                with open(archivoF, "r", encoding="utf-8") as f:
                    datos_archivo = json.load(f)
                print(f"El mes {mes} ya tiene {len(datos_archivo)} días cargados localmente.")
            except Exception as e:
                print(f"Error cargando archivo existente de {mes}: {e}")
                datos_archivo = {}

        # Determinar las fechas que deberían existir para este mes (año 2026)
        month_num = MESES_MAP[mes]
        num_days = calendar.monthrange(2026, month_num)[1]
        all_month_dates = [datetime.date(2026, month_num, d).isoformat() for d in range(1, num_days + 1)]
        
        # Identificar qué fechas faltan en la base de datos o en el JSON local
        missing_dates = [d for d in all_month_dates if d not in dates_in_db and d not in datos_archivo]
        
        if not missing_dates:
            print(f"El mes {mes} está completamente cargado en la BD y localmente. Omitiendo.")
            continue
            
        print(f"Fechas faltantes para {mes}: {missing_dates}")

        # Clasificar los archivos de Google Drive para este mes
        drive_files_by_date = {}
        unparsed_files = []
        
        for archivo in archivos:
            fecha_parsed = parse_date_from_filename(archivo['name'])
            if fecha_parsed:
                drive_files_by_date[fecha_parsed] = archivo
            else:
                unparsed_files.append(archivo)
                
        # Determinar qué archivos necesitamos descargar mapeados por nombre
        files_to_download = []
        for m_date in missing_dates:
            if m_date in drive_files_by_date:
                files_to_download.append((m_date, drive_files_by_date[m_date]))
                
        # Procesar los archivos identificados por nombre
        nuevos_datos_cargados = False
        for f_date, archivo in files_to_download:
            print(f"Descargando archivo específico para {f_date}: {archivo['name']}")
            try:
                wb = hoja_de_trabajo(archivo)
                encabezados, fila_encabezado = leer_encabezados(wb)
                datos_archivo[f_date] = extraer_datos(
                    encabezados,
                    fila_encabezado,
                    wb
                )
                print(f"  -> Día {f_date} cargado exitosamente.")
                nuevos_datos_cargados = True
            except Exception as e:
                print(f"Error procesando {archivo['name']}: {e}")
                errors.append({"file": archivo['name'], "error": f"Error descargando/procesando: {str(e)}"})
                
        # Si aún faltan fechas y tenemos archivos sin parsear por nombre, evaluamos como fallback
        still_missing = [d for d in missing_dates if d not in datos_archivo]
        if still_missing and unparsed_files:
            print(f"Hay {len(still_missing)} fechas faltantes y {len(unparsed_files)} archivos sin fecha legible en el nombre. Evaluando fallbacks...")
            for archivo in unparsed_files:
                try:
                    wb = hoja_de_trabajo(archivo)
                except Exception as e:
                    print(f"Error descargando archivo fallback {archivo['name']}: {e}")
                    errors.append({"file": archivo['name'], "error": f"Error de lectura: {str(e)}"})
                    continue
                    
                # Extraer la fecha del contenido
                fecha_archivo = ""
                for fila in wb.iter_rows():
                    for celda in fila:
                        if (celda.value is not None
                            and "venecia - caqueta" in str(celda.value).lower()
                        ):
                            texto = str(celda.value)
                            m = re.search(r"\d.*", texto)
                            if m:
                                fecha_archivo = re.sub(r'(\d{1,2}),\s+de', r'\1 de', m.group())
                                break
                    if fecha_archivo:
                        break
                        
                if not fecha_archivo:
                    continue
                    
                try:
                    fecha = parse(fecha_archivo).date().isoformat()
                except Exception:
                    continue
                    
                if fecha in still_missing:
                    try:
                        encabezados, fila_encabezado = leer_encabezados(wb)
                        datos_archivo[fecha] = extraer_datos(encabezados, fila_encabezado, wb)
                        print(f"  -> Día {fecha} cargado exitosamente (fallback de contenido).")
                        nuevos_datos_cargados = True
                        still_missing.remove(fecha)
                    except Exception as e:
                        errors.append({"file": archivo['name'], "error": f"Error al extraer estructura: {str(e)}"})

        # Guardar si hubo cambios
        if nuevos_datos_cargados or not archivoF.exists():
            datos_archivo = dict(sorted(datos_archivo.items()))
            print(f"Guardando actualizaciones para el mes {mes}...")
            with open(f"listadoMeses/{mes}.json", "w", encoding="utf-8") as d:
                json.dump(datos_archivo, d, indent=4, ensure_ascii=False, default=str)
        else:
            print(f"No se encontraron nuevos reportes para el mes {mes}.")
            
    return errors

            
def leer_encabezados(hoja):
    CAMPOS = {
        "APELLIDOS Y NOMBRES",
        "CEDULA",
        "SUBNOVEDAD",
        "DESCRIPCION",
        "DESDE",
        "HASTA"
    }

    for fila in hoja.iter_rows(min_row=5, max_row=50):
        encabezados = {}

        for celda in fila:
            if celda.value is None:
                continue

            valor = str(celda.value).strip()

            if valor in CAMPOS:
                encabezados[valor] = {
                    "col": celda.column
                }

        # CEDULA es la columna ancla
        if "CEDULA" in encabezados:
            return encabezados, fila[0].row

    raise ValueError("No se encontró la fila de encabezados.")

def extraer_datos(encabezados, fila_encabezado, hoja):
    datos = {}

    columnas = [
        (nombre, info["col"] - 1)
        for nombre, info in encabezados.items()
    ]

    for fila in hoja.iter_rows(min_row=fila_encabezado + 1):
        indice = fila[0].value

        # Ignorar filas vacías
        if indice is None:
            continue

        registro = {}

        for nombre, columna in columnas:
            registro[nombre] = fila[columna].value

        datos[indice] = registro

    return datos
    

if __name__ == "__main__":
    res = obtener_hojas()