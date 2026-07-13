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

def obtener_hojas():
    # Cargar el listado de archivos agrupados por mes
    with open("listado_meses.json", encoding="utf-8") as l:
        listado_meses = json.load(l)

    errors = []

    # Recorrer cada mes (ENERO, FEBRERO, ...)
    for mes, archivos in listado_meses.items():
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

        # Recorrer todos los Excel del mes
        nuevos_datos_cargados = False
        for archivo in archivos:
            # Intentar abrir el Excel descargado desde Google Drive
            try:
                wb = hoja_de_trabajo(archivo)
            except Exception as e:
                print(f"Error descargando o abriendo {archivo['name']}: {e}")
                errors.append({"file": archivo['name'], "error": f"Error de descarga/lectura: {str(e)}"})
                continue

            fecha_archivo = ""

            # Buscar la fecha escrita en el encabezado del reporte
            for fila in wb.iter_rows():
                for celda in fila:
                    if (celda.value is not None
                        and "venecia - caqueta" in str(celda.value).lower()
                    ):
                        texto = str(celda.value)
                        m = re.search(r"\d.*", texto)

                        if m:
                            fecha_archivo = re.sub(
                                r'(\d{1,2}),\s+de',
                                r'\1 de',
                                m.group()
                            )
                            break

                if fecha_archivo:
                    break

            if not fecha_archivo:
                print(f"No se pudo extraer la fecha de {archivo['name']}")
                errors.append({"file": archivo['name'], "error": "No se pudo extraer la fecha del reporte"})
                continue

            try:
                # Convertir la fecha al formato YYYY-MM-DD
                fecha = parse(fecha_archivo).date().isoformat()
            except Exception as e:
                print(f"Error parseando fecha {fecha_archivo} en {archivo['name']}: {e}")
                errors.append({"file": archivo['name'], "error": f"Fecha inválida o no parseable ({fecha_archivo}): {str(e)}"})
                continue

            # SI YA EXISTE LA FECHA EN EL JSON LOCAL, NO LA SOBREESCRIBIMOS (OMITIMOS)
            if fecha in datos_archivo:
                print(f"  Día {fecha} ya existe localmente. Omitiendo descarga de datos.")
                continue

            try:
                # Obtener las columnas que interesan
                encabezados, fila_encabezado = leer_encabezados(wb)

                # Extraer todos los registros del archivo
                datos_archivo[fecha] = extraer_datos(
                    encabezados,
                    fila_encabezado,
                    wb
                )
                print(f"  -> Nuevo día cargado exitosamente: {fecha}")
                nuevos_datos_cargados = True
            except Exception as e:
                print(f"Error procesando datos de {archivo['name']}: {e}")
                errors.append({"file": archivo['name'], "error": f"Error de estructura o lectura de datos: {str(e)}"})
                continue                

        # Si cargamos nuevos días, volvemos a escribir y ordenar el JSON del mes
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