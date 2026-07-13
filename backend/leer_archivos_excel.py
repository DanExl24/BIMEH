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

    # Recorrer cada mes (ENERO, FEBRERO, ...)
    for mes, archivos in listado_meses.items():
        archivoF = Path(f"listadoMeses/{mes}.json")
        if  archivoF.exists():
            print(f"el mes {mes} ya esta cargado")
            continue
            # Guardar un único JSON para este mes
        # Aquí se almacenarán todos los reportes de ese mes
        # {
        #     "2026-01-01": {...},
        #     "2026-01-02": {...},
        #     ...
        # }
        datos_archivo = {}

        # Recorrer todos los Excel del mes
        for archivo in archivos:

            # Intentar abrir el Excel descargado desde Google Drive
            try:
                wb = hoja_de_trabajo(archivo)
            except Exception as e:
                print(f"Error con {archivo['name']}")
                print(e)
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

            # Convertir la fecha al formato YYYY-MM-DD
            fecha = parse(fecha_archivo).date().isoformat()
            try:
                # Obtener las columnas que interesan
                encabezados, fila_encabezado = leer_encabezados(wb)

                # Extraer todos los registros del archivo
                datos_archivo[fecha] = extraer_datos(
                    encabezados,
                    fila_encabezado,
                    wb
                )
            except Exception as e:
                print(f"Error con encabezados de {archivo['name']}")
                print(e)
                continue                
        # Ordenar los archivos por fecha
        datos_archivo = dict(sorted(datos_archivo.items()))

        print(f"Mes {mes} terminado")
        with open(f"listadoMeses/{mes}.json","w",encoding="utf-8") as d:
            json.dump(datos_archivo,d,indent=4,ensure_ascii=False,default=str)

            
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
    

res = obtener_hojas()