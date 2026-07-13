import os
import json
import sqlite3
from datetime import datetime, timedelta

def get_days_in_month(year, month):
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif month in (4, 6, 9, 11):
        return 30
    elif month == 2:
        # 2026 is not a leap year
        return 28 if year % 4 != 0 else 29
    return 0

def main():
    db_path = "bimej12.db"
    
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop tables if they exist to start fresh
    cursor.execute("DROP TABLE IF EXISTS REGISTRO_PERSONAL;")
    cursor.execute("DROP TABLE IF EXISTS REPORTES;")
    cursor.execute("DROP TABLE IF EXISTS SUB_NOVEDADES;")
    cursor.execute("DROP TABLE IF EXISTS PERSONAL;")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE PERSONAL (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula INTEGER UNIQUE,
        nombre TEXT,
        fecha_retiro TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE SUB_NOVEDADES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE REPORTES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT UNIQUE,
        archivo TEXT
    );
    """)
    
    cursor.execute("""
    CREATE TABLE REGISTRO_PERSONAL (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reporte INTEGER,
        id_personal INTEGER,
        id_sub_novedad INTEGER,
        descripcion TEXT,
        fecha_inicio TEXT,
        fecha_final TEXT,
        FOREIGN KEY (id_reporte) REFERENCES REPORTES(id),
        FOREIGN KEY (id_personal) REFERENCES PERSONAL(id),
        FOREIGN KEY (id_sub_novedad) REFERENCES SUB_NOVEDADES(id)
    );
    """)
    
    print("Tablas creadas exitosamente.")
    
    # 1. Populate PERSONAL table from personal_consolidado.json
    with open("personal_consolidado.json", "r", encoding="utf-8") as f:
        personal_data = json.load(f)
        
    print(f"Cargando {len(personal_data)} registros de personal...")
    for p in personal_data:
        cursor.execute(
            "INSERT INTO PERSONAL (cedula, nombre, fecha_retiro) VALUES (?, ?, ?);",
            (p["cedula"], p["nombre"], p["fecha_retiro"])
        )
    conn.commit()
    print("Tabla PERSONAL poblada.")
    
    # Map cedula to sqlite id for faster lookup
    cursor.execute("SELECT id, cedula FROM PERSONAL;")
    cedula_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Map subnovedad name to sqlite id
    subnovedad_map = {}
    
    months_dir = "listadoMeses"
    month_files = [f for f in os.listdir(months_dir) if f.endswith(".json")]
    
    month_order = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
        "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
        "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }
    
    def get_sort_key(filename):
        name = filename.replace(".json", "").upper()
        return month_order.get(name, 99)
        
    month_files.sort(key=get_sort_key)
    
    log_report = []
    
    # We will track all processed dates to find overall gaps later
    processed_dates = set()
    
    for filename in month_files:
        month_name = filename.replace(".json", "").upper()
        filepath = os.path.join(months_dir, filename)
        
        month_log = {
            "mes": month_name,
            "dias_faltantes": [],
            "dias_duplicados": [],
            "fechas_invalidas": [],
            "reportes_vacios": []
        }
        
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
                continue
        
        # Determine year/month from the data
        month_num = month_order.get(month_name, 1)
        year = 2026  # default based on filename dates
        
        # Find expected dates for this month in the dataset range
        # Let's get the minimum and maximum day present in this month's keys
        month_dates_present = []
        for date_str in data.keys():
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt.month == month_num:
                    month_dates_present.append(dt)
                    processed_dates.add(date_str)
                else:
                    month_log["fechas_invalidas"].append(f"{date_str} (no pertenece a {month_name})")
            except ValueError:
                month_log["fechas_invalidas"].append(date_str)
                
        if month_dates_present:
            min_date = min(month_dates_present)
            max_date = max(month_dates_present)
            
            # Generate all dates from min_date to max_date
            curr = min_date
            while curr <= max_date:
                curr_str = curr.strftime("%Y-%m-%d")
                if curr_str not in data:
                    month_log["dias_faltantes"].append(curr_str)
                curr += timedelta(days=1)
        else:
            month_log["reportes_vacios"].append(f"Sin fechas en {month_name}")
            
        # Process each date
        for date_str, records in data.items():
            if not records:
                month_log["reportes_vacios"].append(date_str)
                continue
                
            # Create Report record
            cursor.execute(
                "INSERT OR IGNORE INTO REPORTES (fecha, archivo) VALUES (?, ?);",
                (date_str, filename)
            )
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (date_str,))
            report_id = cursor.fetchone()[0]
            
            # Track duplicates for this date
            seen_cedulas_for_day = set()
            
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
                    
                if cedula_int not in cedula_map:
                    # Skip if not in personnel DB (should not happen since we consolidated everything)
                    continue
                
                personal_id = cedula_map[cedula_int]
                
                # Check for duplicates on the same date
                if cedula_int in seen_cedulas_for_day:
                    month_log["dias_duplicados"].append(f"Cédula {cedula_int} duplicada en fecha {date_str}")
                    continue
                seen_cedulas_for_day.add(cedula_int)
                
                # Get or Create SubNovedad
                subnovedad_name = record.get("SUBNOVEDAD")
                if subnovedad_name is None:
                    subnovedad_name = "SIN NOVEDAD"
                else:
                    subnovedad_name = str(subnovedad_name).strip().upper()
                    if not subnovedad_name:
                        subnovedad_name = "SIN NOVEDAD"
                
                if subnovedad_name not in subnovedad_map:
                    cursor.execute(
                        "INSERT OR IGNORE INTO SUB_NOVEDADES (nombre) VALUES (?);",
                        (subnovedad_name,)
                    )
                    cursor.execute("SELECT id FROM SUB_NOVEDADES WHERE nombre = ?;", (subnovedad_name,))
                    subnovedad_map[subnovedad_name] = cursor.fetchone()[0]
                    
                subnovedad_id = subnovedad_map[subnovedad_name]
                
                # Clean dates for start and end
                desde = record.get("DESDE")
                hasta = record.get("HASTA")
                
                # Normalize dates to YYYY-MM-DD
                fecha_inicio = None
                if desde:
                    try:
                        fecha_inicio = desde.split()[0]
                    except Exception:
                        pass
                
                fecha_final = None
                if hasta:
                    try:
                        fecha_final = hasta.split()[0]
                    except Exception:
                        pass
                
                # Insert RegistroPersonal
                cursor.execute("""
                INSERT INTO REGISTRO_PERSONAL 
                (id_reporte, id_personal, id_sub_novedad, descripcion, fecha_inicio, fecha_final)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (
                    report_id,
                    personal_id,
                    subnovedad_id,
                    record.get("DESCRIPCION", ""),
                    fecha_inicio,
                    fecha_final
                ))
                
        log_report.append(month_log)
        print(f"Mes {month_name} procesado y guardado en DB.")
        
    conn.commit()
    conn.close()
    
    # Save the log report to processing_report.json for audit and display
    with open("processing_report.json", "w", encoding="utf-8") as f:
        json.dump(log_report, f, indent=4, ensure_ascii=False)
        
    print("\n--- RESUMEN DE PROCESAMIENTO ---")
    for mlog in log_report:
        print(f"Mes: {mlog['mes']}")
        print(f"  Días faltantes ({len(mlog['dias_faltantes'])}): {', '.join(mlog['dias_faltantes'][:5])}{'...' if len(mlog['dias_faltantes']) > 5 else ''}")
        print(f"  Días duplicados (registros duplicados de personas): {len(mlog['dias_duplicados'])}")
        print(f"  Fechas inválidas: {len(mlog['fechas_invalidas'])}")
        print(f"  Reportes vacíos: {len(mlog['reportes_vacios'])}")
        print("-" * 30)
        
    print("Base de datos bimej12.db creada y poblada correctamente.")

if __name__ == "__main__":
    main()
