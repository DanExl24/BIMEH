import os
import json
from datetime import datetime

def main():
    months_dir = "listadoMeses"
    files = [f for f in os.listdir(months_dir) if f.endswith(".json")]
    
    # We want to process them in chronological order
    month_order = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
        "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
        "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }
    
    def get_sort_key(filename):
        name = filename.replace(".json", "").upper()
        return month_order.get(name, 99)
        
    files.sort(key=get_sort_key)
    print(f"Archivos a procesar en orden: {files}")
    
    personnel_db = {}
    all_dates = set()
    
    for filename in files:
        filepath = os.path.join(months_dir, filename)
        print(f"Procesando {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
                continue
                
            for date_str, records in data.items():
                all_dates.add(date_str)
                for rec_id, record in records.items():
                    cedula = record.get("CEDULA")
                    if cedula is None:
                        continue
                    
                    try:
                        cedula_int = int(cedula)
                    except ValueError:
                        continue
                    
                    if cedula_int <= 0:
                        continue
                        
                    nombre = record.get("APELLIDOS Y NOMBRES", "").strip().upper()
                    if not nombre:
                        continue
                        
                    if cedula_int not in personnel_db:
                        personnel_db[cedula_int] = {
                            "cedula": cedula_int,
                            "nombre": nombre,
                            "dates_appeared": set(),
                            "last_record": None
                        }
                    
                    personnel_db[cedula_int]["dates_appeared"].add(date_str)
                    
                    if len(nombre) > len(personnel_db[cedula_int]["nombre"]):
                        personnel_db[cedula_int]["nombre"] = nombre
                        
                    record_date = datetime.strptime(date_str, "%Y-%m-%d")
                    current_last = personnel_db[cedula_int]["last_record"]
                    if current_last is None or record_date > datetime.strptime(current_last["fecha"], "%Y-%m-%d"):
                        personnel_db[cedula_int]["last_record"] = {
                            "fecha": date_str,
                            "subnovedad": record.get("SUBNOVEDAD"),
                            "descripcion": record.get("DESCRIPCION"),
                            "desde": record.get("DESDE"),
                            "hasta": record.get("HASTA")
                        }

    sorted_dates = sorted(list(all_dates))
    if not sorted_dates:
        print("No se encontraron fechas de reportes.")
        return
        
    min_date = sorted_dates[0]
    max_date = sorted_dates[-1]
    print(f"Rango de reportes: desde {min_date} hasta {max_date}. Total días reportados: {len(sorted_dates)}")
    
    consolidated = []
    active_count = 0
    retired_count = 0
    
    for cedula, info in personnel_db.items():
        last_date = max(info["dates_appeared"])
        
        if last_date == max_date:
            status = "ACTIVO"
            fecha_retiro = None
            active_count += 1
        else:
            status = "RETIRADO"
            fecha_retiro = last_date
            retired_count += 1
            
        consolidated.append({
            "cedula": info["cedula"],
            "nombre": info["nombre"],
            "estado": status,
            "fecha_retiro": fecha_retiro,
            "ultimo_registro_fecha": last_date,
            "primer_registro_fecha": min(info["dates_appeared"]),
            "dias_activo": len(info["dates_appeared"])
        })
        
    print(f"Personal consolidado: Total={len(consolidated)}, Activos={active_count}, Retirados={retired_count}")
    
    output_path = "personal_consolidado.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=4, ensure_ascii=False)
    print(f"Guardado exitosamente en {output_path}")

if __name__ == "__main__":
    main()
